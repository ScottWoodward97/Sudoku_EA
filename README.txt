SUDOKU EVOLUTIONARY ALGORITHM README

The evolutionary algorithm requires two command line arguments to run the code;
The first is the population size the algorithm will run with, which must be an integer.
The second is a file (can be .txt or .ss) that contains the sudoku grid. It must be in the following format;

X..!X..!...
X..!XXX!X..
X..!...!.X.
---!---!---
X..!..X!XX.
XXX!X..!..X
..X!X.X!...
---!---!---
XX.!..X!.X.
.XX!.X.!..X
...!X..!XXX

Where the X's are replaced by the digits 1-9 and the .'s represent empty squares.
NOTE: The grid can be in an impossible state (i.e. 2 4's in a box) but the program will never find a solution.
If the grid is not in this format the program will fail to run.

An example command line statement to run the program is as follows;
python sudoku_ea.py 100 Grid1.ss

The program will run 5 experiments on the given Grid and population size and produce a .csv file with plotting the
average best fitness at each generation. Further analysis can be done from here.

NOTE: This code was written in Python 3.5, running in any lower version of python may result in inforeseen errors.