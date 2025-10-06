import unittest
import os
from json import loads as json_loads

from sudokusolver.sudokusolver import SudokuSolver


class SudokuSolverTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_easy(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/easy', 1, 2)

    def test_normal(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/normal', 3, 9)

    def test_hard(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/hard', 91, 99)

    def test_non_standard(self):
        self._test_solve_succeeded(
            SudokuSolver(valid_values={'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'}), 'data/non-standard', 1, 9)

    def test_invalid(self):
        self._test_solve_failed(SudokuSolver(), 'data/invalid')

    def test_multiple_solutions(self):
        self._test_solve_failed(SudokuSolver(), 'data/multiple-solutions')

    def _test_solve_succeeded(self, sudoku_solver, folder, min_level, max_level):
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                grid = sudoku_solver.load(values)
                sudoku_solver.solve(grid)
                self.assertGreaterEqual(grid.level, min_level)
                self.assertLessEqual(grid.level, max_level)

    def _test_solve_failed(self, sudoku_solver, folder):
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                with self.assertRaises(Exception):
                    grid = sudoku_solver.load(values)
                    sudoku_solver.solve(grid)
