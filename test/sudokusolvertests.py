import unittest
import os
from json import loads as json_loads

from sudokusolver.sudokusolver import SudokuSolver


class SudokuSolverTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_easy(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/easy')

    def test_normal(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/normal')

    def test_hard(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/hard')

    def test_non_unique(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/non-unique')

    def test_non_standard(self):
        self._test_solve_succeeded(
            SudokuSolver(valid_values={'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'}), 'data/non-standard')

    def test_invalid(self):
        sudoku_solver, folder = SudokuSolver(), 'data/invalid'
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                with self.assertRaises(Exception):
                    grid = sudoku_solver.load(values)
                    sudoku_solver.solve(grid)

    def _test_solve_succeeded(self, sudoku_solver, folder):
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                grid = sudoku_solver.load(values)
                sudoku_solver.solve(grid)
