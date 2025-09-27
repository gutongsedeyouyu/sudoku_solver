import unittest
import os
from json import loads as json_loads

from sudokusolver.sudokusolver import SudokuSolver


class SudokuSolverTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_easy(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/easy', 9)

    def test_normal(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/normal', 9)

    def test_hard(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/hard', 99)

    def test_non_unique(self):
        self._test_solve_succeeded(SudokuSolver(), 'data/non-unique', 199)

    def test_non_standard(self):
        self._test_solve_succeeded(
            SudokuSolver(valid_values={'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'}), 'data/non-standard', 9)

    def test_invalid(self):
        sudoku_solver, folder = SudokuSolver(), 'data/invalid'
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                with self.assertRaises(Exception):
                    grid = sudoku_solver.load(values)
                    sudoku_solver.solve(grid)

    def _test_solve_succeeded(self, sudoku_solver, folder, max_level):
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                grid = sudoku_solver.load(values)
                sudoku_solver.solve(grid)
                self.assertLessEqual(grid.level, max_level)
