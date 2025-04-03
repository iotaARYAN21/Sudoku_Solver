import pycosat

# Convert (row, column, value) to a unique integer variable.
# We use the formula: 100 * row + 10 * col + value.
# Rows, columns, and values are assumed to be in the range 1 to 9.
def varnum(r, c, v):
    return 100 * r + 10 * c + v

# 1. Each cell contains at least one value.
def cell_at_least_one():
    clauses = []
    for r in range(1, 10):
        for c in range(1, 10):
            clause = [varnum(r, c, v) for v in range(1, 10)]
            clauses.append(clause)
    return clauses

# 2. Each cell contains at most one value.
def cell_at_most_one():
    clauses = []
    for r in range(1, 10):
        for c in range(1, 10):
            for v in range(1, 10):
                for w in range(v + 1, 10):
                    # If cell (r, c) is v then it cannot be w.
                    clauses.append([-varnum(r, c, v), -varnum(r, c, w)])
    return clauses

# 3. Each row contains all the values.
def row_constraints():
    clauses = []
    for r in range(1, 10):
        for v in range(1, 10):
            # At least once in the row.
            clause = [varnum(r, c, v) for c in range(1, 10)]
            clauses.append(clause)
            # At most once in the row.
            for c in range(1, 10):
                for d in range(c + 1, 10):
                    clauses.append([-varnum(r, c, v), -varnum(r, d, v)])
    return clauses

# 4. Each column contains all the values.
def column_constraints():
    clauses = []
    for c in range(1, 10):
        for v in range(1, 10):
            # At least once in the column.
            clause = [varnum(r, c, v) for r in range(1, 10)]
            clauses.append(clause)
            # At most once in the column.
            for r in range(1, 10):
                for s in range(r + 1, 10):
                    clauses.append([-varnum(r, c, v), -varnum(s, c, v)])
    return clauses

# 5. Each 3x3 block contains all the values.
def block_constraints():
    clauses = []
    # For each 3x3 block, use starting row r0 and col c0.
    for r0 in [1, 4, 7]:
        for c0 in [1, 4, 7]:
            for v in range(1, 10):
                # At least one occurrence of v in the block.
                clause = []
                for i in range(3):
                    for j in range(3):
                        clause.append(varnum(r0 + i, c0 + j, v))
                clauses.append(clause)
                # At most one occurrence of v in the block.
                cells = [(r0 + i, c0 + j) for i in range(3) for j in range(3)]
                for idx in range(len(cells)):
                    for jdx in range(idx + 1, len(cells)):
                        r1, c1 = cells[idx]
                        r2, c2 = cells[jdx]
                        clauses.append([-varnum(r1, c1, v), -varnum(r2, c2, v)])
    return clauses

# 6. Add the initial clues from the puzzle.
# The input puzzle is a string with 81 characters (row-major order).
# Empty cells are represented by '.'.
def initial_clauses(puzzle):
    clauses = []
    for i, ch in enumerate(puzzle):
        if ch != '.':
            # Determine row and column from position (i)
            r = i // 9 + 1
            c = i % 9 + 1
            v = int(ch)
            # Add a clause that forces cell (r, c) to be value v.
            clauses.append([varnum(r, c, v)])
    return clauses

# Build the complete CNF from all the constraints.
def build_cnf(puzzle):
    cnf = []
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
    grid = [[0 for _ in range(9)] for _ in range(9)]
    for literal in solution:
        try:
            if literal > 0:
                # Reverse the mapping: varnum = 100*r + 10*c + v.
                v = literal % 10
                c = (literal // 10) % 10
                r = literal // 100
                grid[r - 1][c - 1] = v
        except Exception as e:
            print("Unsatisfiable")
            return grid
    return grid

# Helper function to print the Sudoku grid in a nice format.
def print_grid(grid):
    for row in grid:
        print(" ".join(str(num) for num in row))

# Main function: read puzzles from an input file, solve them, and write results to an output file.
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
                # Convert grid to a single line string (row-major order).
                solved_puzzle = "".join(str(cell) for row in grid for cell in row)
            # Write the solved puzzle to the output file.
            outfile.write(solved_puzzle + "\n")
            print("Solved puzzle:")
            print_grid(decode_solution(solution))
            print("-" * 20)

# Example usage:
if __name__ == '__main__':
    # Replace 'sudoku_input.txt' with your input filename
    input_filename = 'p.txt'
    output_filename = 'sudoku_output.txt'
    solve_sudoku_puzzles(input_filename, output_filename)