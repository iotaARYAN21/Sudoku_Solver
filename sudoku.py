import pycosat

# We use the formula: 100 * row + 10 * col + value.
def cell_encode(r, c, v):   # creating a unique value corresponding to a particular row,col,value
    return 100 * r + 10 * c + v

# 1. Each cell contains at least one value.
def cell_at_least_one():
    clauses = []
    for r in range(1, 10):     #for each row col pair . we are taking values from 1 to 9 and adding it to the clauses as each cell should have a value 
        for c in range(1, 10):  
            clause = []
            for v in range(1, 10):
                clause.append(cell_encode(r, c, v))
            clauses.append(clause)
    return clauses

# 2. Each cell contains at most one value.
def cell_at_most_one():
    clauses = []
    for r in range(1, 10):     # for each row and col either the cell should have v or w as entry 
        for c in range(1, 10): # so for this we are adding the [not a , not b] clause in the clauses list
            for v in range(1, 10):
                for w in range(v + 1, 10):
                    clauses.append([-cell_encode(r, c, v), -cell_encode(r, c, w)])
    return clauses


# 3. Each row contains all the values.
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

# 4. Each column contains all the values.
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

# 5. Each 3x3 block contains all the values.
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

# 6. Add the initial clues from the puzzle.
# The input puzzle is a string with 81 characters .
# Empty cells are represented by '.'.
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

# Build the complete CNF from all the constraints.
def build_cnf(puzzle):
    cnf = []   # adding the clauses according to the condition from the pdf 
    cnf.extend(cell_at_least_one())
    cnf.extend(cell_at_most_one())
    cnf.extend(row_constraints())
    cnf.extend(column_constraints())
    cnf.extend(block_constraints())
    cnf.extend(initial_clauses(puzzle))
    return cnf

# Decode the solution (list of integers) returned by pycosat.
# We extract only the positive integers and map them back to (r, c, v).
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
            print("Unsatisfiable")
            return grid
    return grid


# read puzzles from an input file, solve them, and write results to an output file.
def solve_sudoku_puzzles(input_file, output_file):
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # Process each line (each puzzle)
        for line in infile:
            puzzle = line.strip()
            if not puzzle:
                continue  # skip empty lines
            # Build CNF for this puzzle.
            cnf = build_cnf(puzzle)
            # Use pycosat to solve the CNF.
            solution = pycosat.solve(cnf)
            if solution == "UNSAT":
                solved_puzzle = "No solution"
            else:
                # Decode the solution to a 9x9 grid.
                grid = decode_solution(solution)
                # Convert grid to a single line string
                solved_puzzle = "".join(str(cell) for row in grid for cell in row)
            # Write the solved puzzle to the output file.
            outfile.write(solved_puzzle + "\n")

# Example usage:
# if __name__ == '__main__':
    # Replace 'sudoku_input.txt' with your input filename
input_filename = 'p.txt'
output_filename = 'sudoku_output.txt'
solve_sudoku_puzzles(input_filename, output_filename)