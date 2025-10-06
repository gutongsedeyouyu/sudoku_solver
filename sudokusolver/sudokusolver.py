class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.value = None
        self.candidates = set()
        self.row = None
        self.column = None
        self.square = None


class Grid:
    def __init__(self):
        self.cells = [[Cell(x, y) for x in range(9)] for y in range(9)]
        self.units = list()
        for y in range(9):
            row = list()
            for x in range(9):
                cell = self.cells[y][x]
                row.append(cell)
                cell.row = row
            self.units.append(row)
        for x in range(9):
            column = list()
            for y in range(9):
                cell = self.cells[y][x]
                column.append(cell)
                cell.column = column
            self.units.append(column)
        for y in range(0, 9, 3):
            for x in range(0, 9, 3):
                square = list()
                for dy in range(3):
                    for dx in range(3):
                        cell = self.cells[y + dy][x + dx]
                        square.append(cell)
                        cell.square = square
                self.units.append(square)
        self.level = 0


class SudokuSolver:
    def __init__(self, valid_values=None, log_level=0):
        self.valid_values = set(valid_values) if valid_values else set(str(x) for x in range(1, 10))
        self.log_level = log_level

    def load(self, values):
        grid = Grid()
        for y in range(9):
            for x in range(9):
                cell, value, valid_values = grid.cells[y][x], str(values[y][x]), set(self.valid_values)
                cell.value = value if value in valid_values else None
                cell.candidates = set() if value in valid_values else valid_values
        for unit in grid.units:
            unit_values = [c.value for c in unit if c.value]
            if len(unit_values) > len(set(unit_values)):
                raise Exception('Failed to load the grid, duplicate values found in a unit.')
        return grid

    def solve(self, grid):
        grid.level = 1
        self._solve_1(grid)
        if not self._is_finished(grid):
            for i in range(2, 9):
                grid.level = i
                for j in range(i, 1, -1):
                    self._solve_n(grid, j)
                if self._is_finished(grid):
                    break
        if not self._is_finished(grid):
            grid.level = 90
            solutions = self._solve_by_guessing(grid)
            if solutions:
                self._copy_grid(solutions[0], grid)
        if not self._is_finished(grid) or not self._is_valid(grid):
            raise Exception('The grid has no solution.')

    def write_to_console(self, grid):
        print('-------------------------------')
        print('|          Level {:02d}           |'.format(grid.level))
        print('|-----------------------------|')
        for y in range(9):
            if y % 3 == 0 and y != 0:
                print('|---------+---------+---------|')
            row, row_str = grid.cells[y], '| '
            for x in range(9):
                row_str += '  |  ' if x % 3 == 0 and x != 0 else ' '
                row_str += row[x].value if row[x].value else '·'
            row_str += '  |'
            print(row_str)
        print('-------------------------------')

    def _solve_1(self, grid):
        for row in grid.cells:
            for cell in row:
                if cell.value:
                    self._set_value(cell, cell.value, grid.level)

    def _solve_n(self, grid, n):
        while True:
            any_progress = False
            # Solve inside each unit.
            for unit in grid.units:
                cells = [c for c in unit if not c.value]
                if len(cells) < n:
                    continue
                indexes = [_ for _ in range(n)]
                while True:
                    candidates = set()
                    for i in indexes:
                        candidates = candidates.union(cells[i].candidates)
                    if len(candidates) == n:
                        for i in range(len(cells)):
                            if i in indexes:
                                continue
                            for candidate in candidates:
                                if candidate in cells[i].candidates:
                                    self._remove_candidate(cells[i], candidate, grid.level)
                                    any_progress = True
                    if any_progress:
                        break
                    if indexes[0] == len(cells) - n:
                        break
                    for i in range(n - 1, -1, -1):
                        if indexes[i] < len(cells) - n + i:
                            indexes[i] += 1
                            for j in range(i + 1, n):
                                indexes[j] = indexes[j - 1] + 1
                            break
            # Solve cross units.
            for unit in grid.units:
                value_cells_dict = {v: set(c for c in unit if v in c.candidates) for v in self.valid_values}
                for value, cells in value_cells_dict.items():
                    if len(cells) == 0:
                        continue
                    if len(cells) == 1:
                        self._set_value(list(cells)[0], value, grid.level)
                        any_progress = True
                        continue
                    shared_row, shared_column, shared_square = None, None, None
                    for i, cell in enumerate(cells):
                        if i == 0:
                            shared_row, shared_column, shared_square = cell.row, cell.column, cell.square
                        else:
                            if shared_row is not cell.row:
                                shared_row = None
                            if shared_column is not cell.column:
                                shared_column = None
                            if shared_square is not cell.square:
                                shared_square = None
                    for shared_unit in (shared_row, shared_column, shared_square):
                        if shared_unit:
                            for other_cell in shared_unit:
                                if other_cell not in cells and value in other_cell.candidates:
                                    self._remove_candidate(other_cell, value, grid.level)
                                    any_progress = True
            # Solve n is done if not making any progress.
            if not any_progress:
                break

    def _solve_by_guessing(self, grid, solutions=None):
        if solutions is None:
            solutions = list()
        grid.level += 1
        guessing_cell = None
        for row in grid.cells:
            for cell in row:
                if cell.value:
                    continue
                if not guessing_cell or len(guessing_cell.candidates) > len(cell.candidates):
                    guessing_cell = cell
        for candidate in list(guessing_cell.candidates):
            guessing_grid = Grid()
            self._copy_grid(grid, guessing_grid)
            self._set_value(guessing_grid.cells[guessing_cell.y][guessing_cell.x], candidate, guessing_grid.level)
            for i in range(2, 9):
                for j in range(i, 1, -1):
                    self._solve_n(guessing_grid, j)
                if self._is_finished(guessing_grid):
                    break
            if not self._is_finished(guessing_grid):
                self._solve_by_guessing(guessing_grid, solutions)
            elif not self._is_valid(guessing_grid):
                self._log('Incorrect :-(')
            else:
                self._log('Correct :-)')
                if len(solutions) > 0:
                    raise Exception('The grid has multiple solutions.')
                solutions.append(guessing_grid)
        return solutions

    def _set_value(self, cell, value, level):
        if not cell.value:
            self._log(f'{level}: ({cell.x + 1}, {cell.y + 1}) == {value}')
        cell.value = value
        cell.candidates.clear()
        for unit in (cell.row, cell.column, cell.square):
            for other_cell in unit:
                if other_cell is not cell and value in other_cell.candidates:
                    self._remove_candidate(other_cell, value, level)

    def _remove_candidate(self, cell, candidate, level):
        self._log(f'{level}: ({cell.x + 1}, {cell.y + 1}) != {candidate}', level=2)
        cell.candidates.remove(candidate)
        if len(cell.candidates) == 1:
            self._set_value(cell, cell.candidates.pop(), level)

    def _copy_grid(self, from_grid, to_grid):
        for y in range(9):
            for x in range(9):
                to_grid.cells[y][x].value = from_grid.cells[y][x].value
                to_grid.cells[y][x].candidates = set(from_grid.cells[y][x].candidates)
        to_grid.level = from_grid.level

    def _is_finished(self, grid):
        return all(all(c.value for c in r) for r in grid.cells)

    def _is_valid(self, grid):
        for unit in grid.units:
            if len(set(c.value for c in unit)) < 9:
                return False
        return True

    def _log(self, message, level=1):
        if self.log_level >= level:
            print(message)
