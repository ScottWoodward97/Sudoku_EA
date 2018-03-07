from random import choice, randint, shuffle, random
from copy import deepcopy
import sys
from timeit import default_timer as timer
import csv

##PROGRAM CONSTANTS##
MODEL_SET = {1,2,3,4,5,6,7,8,9}
TRUNCATION_RATE = 0.50   
MUTATION_RATE = 0.25
NUMBER_GENERATION = 250



##FILE PROCESSING##
def process_file(fileName):
	"""
	process_file will open a given file and process the grid state so that it can
	be managed within the program
	Param:	fileName is the path of the file being used.
	The function will return the grid in the desired format and will crash if it is not
	in the desired format.
	"""
	with open(fileName) as f:
		grid = [[],[],[],[],[],[],[],[],[]]
		i = 0
		for x, line in enumerate(f):
			if x!= 3 and x!= 7:
				for n,a in enumerate(line):
					#Add the value read into the respective location in the grid
					if n < 3:
						#Replace any '.'s with 0's
						if a == '.':
							a = 0
						grid[i].append(int(a))
					elif 3 < n < 7:
						if a == '.':
							a = 0
						grid[i+1].append(int(a))
					elif 7 < n < 11:
						if a == '.':
							a = 0
						grid[i+2].append(int(a))
			else:
				i+=3
	return grid
	
##EVOLUTIONARY ALGORITHM##	
def evolve(grid):
	"""
	evolve performs an evolutionary algorithm to attempt to solve the given grid.
	Evolutionary algorithm runs until a solution is found, 250 generation have been created,
	or 5 minutes has elapsed.
	The function will print out the generation it exited at, the best fitness of that generation,
	the time taken to compute, and the best solution.
	
	Param: grid is the grid for which the solution exists in.
	Returns: A list of the results, the best fitness for each generation, for later analysis
	"""
	results = [0]*(NUMBER_GENERATION+1)
	
	start = timer()
	gen,end = 0,0
	
	#Creates the initial population
	population = create_pop(grid)
	fitness_population = evaluate_pop(population)
	results[gen] = sorted(fitness_population)[0]

	while gen < NUMBER_GENERATION and timer() < start + (60*5):

		mating_pool = select_pop(deepcopy(population), fitness_population, POPULATION_SIZE*TRUNCATION_RATE)
		
		#Create child solutions from the selected parents
		offspring = crossover_pop(mating_pool)
		offspring = mutate_pop(offspring)	
		fitness_offspring = evaluate_pop(offspring)
			
		#Determine if all offspring are worse than the current population
		if shouldMerge(fitness_offspring, fitness_population):
			#If so, creates a new population from the best 50% of the children and the entire population
			best_off = select_pop(offspring, fitness_offspring, POPULATION_SIZE*TRUNCATION_RATE)
			best_off_fit = evaluate_pop(best_off)
			population = select_pop(deepcopy(population + best_off), fitness_population + best_off_fit, POPULATION_SIZE)
			fitness_population = evaluate_pop(population)
			
		best_ind, best_fit = best_pop(population, fitness_population)
		gen += 1
		#Store the data in the results list
		results[gen] = best_fit
		
		if best_fit == 0:
			break	
	
	end = timer()
	#Print out the information for the user
	print("Generation: %3d" % gen, " Fitness :%3d" % best_fit)
	print("Time taken: %.2fs" % (end-start))
	print("Best Solution Found:\n",best_ind, "\n")
	
	return results
	
##POPULATION WIDE##
def create_pop(grid):
	"""
	create_pop creates the initial population
	Param: grid - The grid that the solution exists in
	Returns: A list of potential solutions
	"""
	return [create_ind(grid) for _ in range(POPULATION_SIZE)]

def evaluate_pop(population):
	"""
	evaluate_pop evaluates the fitness of each item in the population
	Param: population - A list of potential solutions
	Returns: A list of fitness values
	"""
	return [ evaluate_ind(individual) for individual in population ]

def select_pop(population, fitness_population, size):
	"""
	select_pop determines the best from a given population
	Param: population - A list of potential solutions
		   fitness_population - The corresponding list of fitness values
		   size - An integer determining the number to return
	Returns: A truncated list of solutions
	"""
	sorted_population = sorted(zip(population, fitness_population), key = lambda ind_fit: ind_fit[1])
	return [ individual for individual, fitness in sorted_population[:int(size)] ]

def crossover_pop(population):
	"""
	crossover_pop creates a child population from the parent population
	Param: population - A list of potential solutions
	Returns: A list of new potential solutions
	"""
	return [ crossover_ind(choice(population), choice(population)) for _ in range(POPULATION_SIZE) ]

def mutate_pop(population):
	"""
	mutate_pop individually mutates each item in the given population
	Param: population - A list of potential solutions
	Returns: A list of mutated potential solutions
	"""
	return [mutate_ind(individual) for individual in population]

def best_pop(population, fitness_population):
	"""
	best_pop finds the best item in the given population
	Param: population - A list of potential solutions
		   fitness_population - The corresponding list of fitness values
	"""
	return sorted(zip(population, fitness_population), key = lambda ind_fit: ind_fit[1])[0]
	
def shouldMerge(offspring_fit, population_fit):
	"""
	shouldMerge determines if the entire child population is
	worse than the parent population
	Param: offspring_fit, population_fit - Lists of fitness values
	Returns: False if the entire child population is worse
	"""
	best_off_fit = sorted(offspring_fit)[0]
	worst_pop_fit = sorted(population_fit)[-1]
	return best_off_fit < worst_pop_fit	

##INDIVIDUAL##	
def create_ind(grid):
	"""
	create_ind will create a random potential solution for the given grid.
	This function reads the grid and only adds those values that have not been
		given in the grid.
	Param: grid - The grid for which the solution exists within
	Returns: A single potential solution for grid
	"""
	l = []
	for a in range(9):
		g = deepcopy(grid[a])
		
		#Determines all the indices where values need to be inserted
		inds = [j for j in range(9) if g[j]==0]
		#Determines what values are missing from the current box
		vals = list(MODEL_SET - set([e for e in g if e != 0]))
		
		#Randomises the order of both lists
		shuffle(inds)
		shuffle(vals)
		for i,v in zip(inds, vals):
			g[i] = v
			
		l.append(g)
	return l
	
def evaluate_ind(individual):
	"""
	evaluate_ind will determine the fitness function of a given potential solution.
	Uses list splicing to create each row and column, then converts the constructed list to 
		a set to remove its duplicates. Using the length of this set allows for the number 
		of duplicate entries to be determined
	Param: individual - A potential solution
	Returns: An integer representing its fitness value
	"""
	tot = 0
	for a in range(0,3):
		for b in range(0,3):			
			#Determines the number of duplicates in a row
			tot += 9 - len(set(individual[3*b][3*a:3*(a+1)]+individual[3*b+1][3*a:3*(a+1)]+individual[3*b+2][3*a:3*(a+1)]))
			#Determines the number of duplicates in a column
			tot += 9 - len(set(individual[b][a::3]+individual[b+3][a::3]+individual[b+6][a::3]))
	return tot	
	
def crossover_ind(grid1, grid2):
	"""
	crossover_ind creates a child solution from two parents.
	Each box in the child solution is inherited from one of the two parents selected at random
	Param: grid1, grid2 - Two potential solutions
	Returns: A new child solution
	"""
	return [ choice(box) for box in zip(grid1, grid2) ]

def mutate_ind(individual):
	"""
	mutate_ind returns a mutated copy of the solution passed in.
	Each 'box' in the solution has a 25% chance of mutating, and a mutation involves the
		swapping of two values. The only values that can be mutated are those that are not
		defined in the grid.
	Param: individual - A single potential solution
	Returns: A mutated copy of individual
	"""
	t = deepcopy(individual)
	for i in range(9):
		if random() < MUTATION_RATE:
			g = grid[i]
			#Determines the indices that can be mutated
			inds = [j for j in range(9) if g[j]==0 or t[i][j] != g[j]]
			if len(inds) > 1:
				#Select two unique indices and swap them
				a,b = choice(inds), choice(inds)
				while (b==a):
					b = choice(inds)
				t[i][a], t[i][b] = t[i][b], t[i][a]		
	return t

##MAIN##	
if __name__ == "__main__":
	"""
	This is the main method of the program and will run when called in the command line.
	The program requires, as command line arguments, the population size as an integer, and the path
		of the file containing the grid.
	
	This will run 5 experiments of the evolutionary algorithm, storing the results of each, before calculating
		the average across them.
	The results store the best fitness at each generation.
	These results are then exported to a .csv file, with a name related to the parameters passed in, for further analysis
	"""
	POPULATION_SIZE = int(sys.argv[1])
	fileName = sys.argv[2]
	grid = process_file(fileName)

	#Initialisation of the results table
	results = [["Generation No", "Average Fitness"]]
	[results.append([i]) for i in range(NUMBER_GENERATION+1)]
	
	r1 = evolve(grid)
	r2 = evolve(grid)
	r3 = evolve(grid)
	r4 = evolve(grid)
	r5 = evolve(grid)
	
	#Calcuates the averages at each generation
	for i in range(0, NUMBER_GENERATION+1):
		s = (r1[i]+r2[i]+r3[i]+r4[i]+r5[i])/5
		results[i+1].append(s)
		if s == 0:
			break
			
	#Truncates the results if and once every algorithm has arrived at a correct solution 
	results = results[:i+2]
	
	resultFileName = fileName.rsplit(".",1)[0] + '-POP' + sys.argv[1] +'-EvolutionResults.csv'
	
	#Writes the results to a .csv file
	with open(resultFileName, 'w', newline='') as csvfile:
		writer = csv.writer(csvfile)
		[writer.writerow(r) for r in results]
		
	print("Results sotred and saved in " + resultFileName)
	