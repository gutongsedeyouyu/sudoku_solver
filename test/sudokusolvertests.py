import unittest
import os
from json import loads as json_loads

from sudokusolver.sudokusolver import SudokuSolver


class SudokuSolverTest(unittest.TestCase):
    def setUp(self):
        self.sudoku_solver = SudokuSolver()

    def test_easy(self):
        self._test_solve_succeeded('data/easy')

    def test_normal(self):
        self._test_solve_succeeded('data/normal')

    def test_hard(self):
        self._test_solve_succeeded('data/hard')

    def test_non_unique(self):
        self._test_solve_succeeded('data/non-unique')

    def test_invalid(self):
        folder = 'data/invalid'
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                with self.assertRaises(Exception):
                    grid = self.sudoku_solver.load(values)
                    self.sudoku_solver.solve(grid)

    def _test_solve_succeeded(self, folder):
        for file_name in os.listdir(folder):
            with open(os.path.join(folder, file_name)) as file:
                values = json_loads(file.read())
                grid = self.sudoku_solver.load(values)
                self.sudoku_solver.solve(grid)
