from json import loads as json_loads

from sudokusolver.sudokusolver import SudokuSolver


def main():
    solver = SudokuSolver(log_level=1)
    with open('values.json') as file:
        try:
            values = json_loads(file.read())
            grid = solver.load(values)
            solver.solve(grid)
            solver.write_to_console(grid)
        except Exception as e:
            raise e


if __name__ == '__main__':
    main()
