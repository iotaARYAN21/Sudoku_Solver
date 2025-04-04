# Sudoku Solver using pycosat
## Team Members
    1. Aryan        112301041
    2. Varun Jha    112301036

## Requirements 

- pycosat
    `pip install pycosat`

## Running the script
**Note :** Make sure you are in the folder containing sudoku.py and p.txt (the input file)
- For Windows `python sudoku.py`
- For Linux `python3 sudoku.py`

## Output

**Example**

**Input** 
....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1..

**Output**
957261384846537921123489567734926815295814736618375492572198643481653279369742158

***

**Input**
....6...4..6.3....1..4..5.77.....8.5...8.....6.8....9...2.9....4....32....97..1.1

**Output**
No solution


## Code Explaination

### cell_encode(r,c,v)
<pre>
def cell_encode(r, c, v):   # creating a unique value corresponding to a particular row,col,value
    return 100 * r + 10 * c + v
</pre>

This function generates a unique integer identifier for a given cell and value in the Sudoku grid using the formula 100 * row + 10 * column + value. This encoding is used to represent each possible assignment in the SAT solver.

###  cell_at_least_one()
<pre>
def cell_at_least_one():
    clauses = []
    for r in range(1, 10):     #for each row col pair . we are taking values from 1 to 9 and adding it to the clauses as each cell should have a value 
        for c in range(1, 10):  
            clause = []
            for v in range(1, 10):
                clause.append(cell_encode(r, c, v))
            clauses.append(clause)
    return clauses
</pre>

The cell_at_least_one() function makes sure that every cell in the Sudoku grid has at least one number between 1 and 9. It does this by going through every row and column, and for each cell, it creates a list of variables representing the possible values that cell can take (from 1 to 9). This list is added as a clause to the CNF, which means that the SAT solver must assign at least one of those values to that cell

### cell_at_most_one()
<pre>
def cell_at_most_one():
    clauses = []
    for r in range(1, 10):     # for each row and col either the cell should have v or w as entry 
        for c in range(1, 10): # so for this we are adding the [not a , not b] clause in the clauses list
            for v in range(1, 10):
                for w in range(v + 1, 10):
                    clauses.append([-cell_encode(r, c, v), -cell_encode(r, c, w)])
    return clauses
</pre>

This function ensures that each cell in the Sudoku grid contains at most one number from 1 to 9. For every cell at position (row, column), it goes through all pairs of different possible values (v, w) and adds a clause that says: if the cell has value v, then it cannot have value w. In CNF form, this is written as [-v, -w]. These pairwise constraints prevent the SAT solver from assigning more than one number to the same cell

### row_constraints()

<pre>
def row_constraints():
    clauses = []
    for r in range(1, 10):   # for each row .. we are traversing over all the 9 numbers and for all the column values,, adding the clause to the clauses list 
        for v in range(1, 10):   # and to ensure that each value is once in the list we are taking the negation of that cell encoding with the all the other cell encoding for that row
            clause = []          
            for c in range(1, 10):
                clause.append(cell_encode(r, c, v))
            clauses.append(clause)
            
            for c1 in range(1, 10):
                for c2 in range(c1 + 1, 10):
                    clauses.append([-cell_encode(r, c1, v), -cell_encode(r, c2, v)])
    return clauses
</pre>

This function ensures that every row in the Sudoku grid contains all the numbers from 1 to 9 exactly once. For each row and each number, it first creates a clause that allows the number to appear in at least one of the columns in that row. Then, to make sure the number doesn't appear more than once in that row, it adds pairwise clauses between all column positions saying that the number cannot be in both columns at the same time. This prevents duplication of the same number in the same row.

### column_constraints()

<pre>
def column_constraints():
    clauses = []
    for c in range(1, 10):   # for each col .. we are traversing over all the 9 numbers and for all the row values,, adding the clause to the clauses list
        for v in range(1, 10):# and to ensure that each value is once in the list we are taking the negation of that cell encoding with the all the other cell encoding for that col
            clause = []
            for r in range(1, 10):
                clause.append(cell_encode(r, c, v))
            clauses.append(clause)
            
            for r1 in range(1, 10):
                for r2 in range(r1 + 1, 10):
                    clauses.append([-cell_encode(r1, c, v), -cell_encode(r2, c, v)])
    return clauses
</pre>

This function makes sure that each column in the Sudoku grid contains all numbers from 1 to 9 exactly once. For every column and each number, it first adds a clause that allows the number to appear in at least one of the rows in that column. Then, to prevent the same number from appearing more than once in the column, it adds clauses for every pair of different rows, saying that the number cannot appear in both rows at the same time.

### block_constraints()
<pre>
def block_constraints():
    clauses = []
    for r0 in [1, 4, 7]: #traversing over the starting position i.e. the top left cell of all the 3x3 subgrid
        for c0 in [1, 4, 7]:   # similarly for the column
            for v in range(1, 10):
                clause = []
                cells = []
                for i in range(3):    # for each cell adding a triplet cell encoding to the clauses 
                    for j in range(3): # and maintaining a separate cell list to ensure that each value occurs in a 3x3 subgrid once only
                        clause.append(cell_encode(r0 + i, c0 + j, v))
                        cells.append((r0 + i, c0 + j))
                clauses.append(clause)
                
                for idx in range(len(cells)):
                    for jdx in range(idx + 1, len(cells)):
                        r1, c1 = cells[idx]
                        r2, c2 = cells[jdx]
                        clauses.append([-cell_encode(r1, c1, v), -cell_encode(r2, c2, v)])  # v should occur in the 3x3 subgrid once only
    return clauses
</pre>

This function ensures that each 3x3 block in the Sudoku grid contains all digits from 1 to 9 exactly once. It iterates over the starting positions of each 3x3 block and, for each number, adds a clause that allows the number to appear somewhere in the block. To enforce that the number appears only once, it creates clauses that prevent the number from being in two different cells within the same block at the same time. This guarantees both the presence and uniqueness of each digit in every 3x3 subgrid.

### initial_clauses(puzzle)

<pre>
def initial_clauses(puzzle):
    clauses = []
    for i in range(len(puzzle)):
        ch = puzzle[i]
        if ch != '.':
            r = (i // 9) + 1  # formula to get the row value from the puzzle 
            c = (i % 9) + 1  # formula to get the col value from the puzzle
            v = int(ch)  # traversing over the puzzle grid and if the cell contains a particular value then adding the encoding corresponding to it to the clauses 
            clauses.append([cell_encode(r, c, v)])
    return clauses
</pre>

This function processes the initial Sudoku puzzle input, where each puzzle is represented as a string of 81 characters in row-major order. It scans each character, and if it represents a digit (i.e., a clue), it calculates the corresponding row and column indices. Then, it adds a clause that forces the cell at that position to take the given value. This encodes the fixed starting numbers into the CNF formula to be used by the SAT solver.


### build_cnf(puzzle)

<pre>
def build_cnf(puzzle):
    cnf = []   # adding the clauses according to the condition from the pdf 
    cnf.extend(cell_at_least_one())
    cnf.extend(cell_at_most_one())
    cnf.extend(row_constraints())
    cnf.extend(column_constraints())
    cnf.extend(block_constraints())
    cnf.extend(initial_clauses(puzzle))
    return cnf
</pre>

This function calls all the functions corresponding to the constraints of the sudoku puzzle and creates corresponding clauses which is then added to the cnf list.

### decode_solution(solution)

<pre>
def decode_solution(solution):
    # Create a 9x9 grid filled with 0s.
    grid = [[0 for row in range(9)] for col in range(9)]
    # print(solution)
    for literal in solution: 
        try:
            if literal > 0:
                # Reverse the mapping: cell_encode = 100*r + 10*c + v.
                v = literal % 10
                c = (literal // 10) % 10
                r = literal // 100
                grid[r - 1][c - 1] = v
        except Exception as e:
            return grid
    return grid
</pre>

This function takes the solution returned by the SAT solver, which is a list of integers representing true variables in the CNF formula. Each positive integer corresponds to a (row, column, value) triplet using the encoding formula. The function decodes each such variable back to its row, column, and value, and fills a 9x9 Sudoku grid accordingly. The resulting grid represents the solved Sudoku puzzle.If the puzzle solution is not possible then if it compares a dot(.) with 0  then it will give incompatible comparison error between string and int value which is handled by the try except block.
