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
        self.level = 0
        self._post_init()

    def _post_init(self):
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


class SudokuSolver:
    def __int__(self):
        pass

    def load(self, values):
        grid = Grid()
        for y in range(9):
            for x in range(9):
                cell, value, valid_values = grid.cells[y][x], str(values[y][x]), self._valid_values()
                cell.value = value if value in valid_values else None
                cell.candidates = set() if value in valid_values else valid_values
        for unit in grid.units:
            unit_values = [c.value for c in unit if c.value]
            if len(unit_values) > len(set(unit_values)):
                raise Exception('Duplicate values found in a unit.')
        return grid

    def solve(self, grid):
        grid.level = 1
        self._solve_1(grid)
        if not self._is_finished(grid):
            for i in range(2, 9):
                grid.level = i
                for j in range(i, 1, -1):
                    self._solve_n_within_unit(grid, j)
                    self._solve_n_cross_units(grid, j)
                if self._is_finished(grid):
                    break
        if not self._is_finished(grid):
            grid.level = 99
            guessing_grid = self._solve_by_guessing(grid)
            if guessing_grid:
                self._copy_grid(guessing_grid, grid)
        if not self._is_finished(grid) or not self._is_valid(grid):
            raise Exception('Unable to solve the grid.')

    def write_console(self, grid):
        print('<<< Level: {:02d} >>>'.format(grid.level))
        print('\n'.join(' '.join(c.value if c.value else '·' for c in r) for r in grid.cells))
        if grid.level > 0 and not self._is_finished(grid):
            for y in range(9):
                print('----- Line {} -----'.format(y + 1))
                for x in range(9):
                    cell = grid.cells[y][x]
                    print(cell.value if cell.value else sorted(cell.candidates))

    def _valid_values(self):
        return set(str(x) for x in range(1, 10))

    def _solve_1(self, grid):
        for unit in grid.units:
            for cell in unit:
                if cell.value:
                    self._set_value(cell, cell.value)

    def _solve_n_within_unit(self, grid, n):
        while True:
            any_progress = False
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
                                    self._remove_candidate(cells[i], candidate)
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
            if not any_progress:
                break

    def _solve_n_cross_units(self, grid, n):
        while True:
            any_progress = False
            for unit in grid.units:
                value_cells_dict = {v: set(c for c in unit if v in c.candidates) for v in self._valid_values()}
                for value, cells in value_cells_dict.items():
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
                                    self._remove_candidate(other_cell, value)
                                    any_progress = True
            if not any_progress:
                break

    def _solve_by_guessing(self, grid):
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
            self._set_value(guessing_grid.cells[guessing_cell.y][guessing_cell.x], candidate)
            for i in range(2, 9):
                for j in range(i, 1, -1):
                    self._solve_n_within_unit(guessing_grid, j)
                    self._solve_n_cross_units(guessing_grid, j)
                    if self._is_finished(guessing_grid) and self._is_valid(guessing_grid):
                        return guessing_grid
            if not self._is_finished(guessing_grid):
                further_guessing_grid = self._solve_by_guessing(guessing_grid)
                if further_guessing_grid:
                    return further_guessing_grid
        return None

    def _set_value(self, cell, value):
        cell.value = value
        cell.candidates.clear()
        for unit in (cell.row, cell.column, cell.square):
            for other_cell in unit:
                if other_cell is not cell and value in other_cell.candidates:
                    other_cell.candidates.remove(value)
                    if len(other_cell.candidates) == 1:
                        self._set_value(other_cell, other_cell.candidates.pop())

    def _remove_candidate(self, cell, candidate):
        cell.candidates.remove(candidate)
        if len(cell.candidates) == 1:
            cell.value = cell.candidates.pop()
            for unit in (cell.row, cell.column, cell.square):
                for other_cell in unit:
                    if other_cell is not cell and cell.value in other_cell.candidates:
                        self._remove_candidate(other_cell, cell.value)

    def _copy_grid(self, from_grid, to_grid):
        for y in range(9):
            for x in range(9):
                to_grid.cells[y][x].value = from_grid.cells[y][x].value
                to_grid.cells[y][x].candidates = set(from_grid.cells[y][x].candidates)

    def _is_finished(self, grid):
        return all(all(c.value for c in r) for r in grid.cells)

    def _is_valid(self, grid):
        for unit in grid.units:
            if len(set(c.value for c in unit)) < 9:
                return False
        return True
