# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-corner-table-min-ltelte/template.py
# @operations: minAll minLteLte
# @data-structure-type: corner-table
# @input: grid
# @complexities:
#   minAll: 1
#   minLteLte: 1
#   build: R*C
# @memory:
#   layout: none
#   node: tLteLte[1*R*C]
#   tags: none
#   other: none
#   note: one R by C table per corner direction, flat



# Static corner min: the min over a corner of the grid (every cell with row <= r or >= r, and column <= c or >= c) in
# O(1), from one R x C table per direction filled in a single pass (a cell's corner is its own row's running min
# joined with the corner of the cell one row back). No updates. Rows and columns are 0-based.
class CornerMinTable2D:
    __slots__ = ("R", "C", "best", "tLteLte")

    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("CornerMinTable2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        self.best = min(min(row) for row in grid)
        t = self.tLteLte = [0] * (R * C)
        for r in range(R):
            row = grid[r]
            at = r * C
            run = row[0]
            if r > 0:
                back = at - C
                for c in range(C):
                    v = row[c]
                    if v < run:
                        run = v
                    x = t[back + c]
                    t[at + c] = run if run < x else x
            else:
                for c in range(C):
                    v = row[c]
                    if v < run:
                        run = v
                    t[at + c] = run

    # O(1) -- min of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def minLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.tLteLte[r * self.C + c]

    # O(1) -- min of the whole grid
    def minAll(self):
        return self.best
