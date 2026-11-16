# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-sparse-table-max/template.py
# @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointGet rectMax squareMax
# @data-structure-type: sparse-table
# @input: grid
# @complexities:
#   maxAll: 1
#   maxGteGte: 1
#   maxGteLte: 1
#   maxLteGte: 1
#   maxLteLte: 1
#   pointGet: 1
#   rectMax: 1
#   squareMax: 1
#   build: R*C*log(R)*log(C)
# @memory:
#   layout: none
#   node: mx[1*R*C*log(R)*log(C)]
#   tags: none
#   other: none
#   note: per aggregate, one table for every pair of a power-of-two height and a power-of-two width (the 1 x 1 table is the grid itself, shared)



# Static 2D sparse table (max): any rectangle in O(1). For every power-of-two height and power-of-two width there is a
# table holding the aggregate of each window of that size; a rectangle is covered by four such windows, one in each
# corner (they overlap, which is fine: each of these gives the same answer when a cell is counted twice). Memory and
# build are R * C * log R * log C: when only squares are asked for, the square sparse table needs a single log. No
# updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class SparseTable2D:
    __slots__ = ("R", "C", "mx")

    # O(R*C*logR*logC) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SparseTable2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        flat = [v for row in grid for v in row]
        levelsR = R.bit_length()
        levelsC = C.bit_length()
        t = self.mx = [[None] * levelsC for _ in range(levelsR)]  # t[kr][kc]: windows of 2^kr rows by 2^kc columns
        t[0][0] = flat
        for kc in range(1, levelsC):
            half = 1 << (kc - 1)
            prevW = C - half + 1
            prev = t[0][kc - 1]
            cur = []
            for r in range(R):
                seg = prev[r * prevW:(r + 1) * prevW]
                cur += [x if x > y else y for x, y in zip(seg, seg[half:])]
            t[0][kc] = cur
        for kr in range(1, levelsR):
            half = 1 << (kr - 1)
            for kc in range(levelsC):
                prev = t[kr - 1][kc]
                off = half * (C - (1 << kc) + 1)
                t[kr][kc] = [x if x > y else y for x, y in zip(prev, prev[off:])]

    def _maxOf(self, r1, c1, r2, c2):
        kr = (r2 - r1 + 1).bit_length() - 1
        kc = (c2 - c1 + 1).bit_length() - 1
        t = self.mx[kr][kc]
        w = self.C - (1 << kc) + 1
        i = r1 * w + c1
        j = (r2 - (1 << kr) + 1) * w + c1
        d = c2 - (1 << kc) + 1 - c1
        return max(t[i], t[i + d], t[j], t[j + d])

    # O(1) -- max of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectMax(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._maxOf(r1, c1, r2, c2)

    # O(1) -- max of the square with top-left cell (r, c) and that many rows and columns; needs side >= 1 and the square
    # inside the grid, else IndexError
    def squareMax(self, r, c, side):
        if not (side >= 1 and 0 <= r and r + side <= self.R and 0 <= c and c + side <= self.C):
            raise IndexError(f"squareMax: needs side >= 1 and the square inside the grid, got r = {r}, c = {c}, "
                             f"side = {side}, R = {self.R}, C = {self.C}")
        return self._maxOf(r, c, r + side - 1, c + side - 1)

    # O(1) -- max of the whole grid
    def maxAll(self):
        return self._maxOf(0, 0, self.R - 1, self.C - 1)

    # O(1) -- max of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def maxLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(0, 0, r, c)

    # O(1) -- max of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def maxLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(0, c, r, self.C - 1)

    # O(1) -- max of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def maxGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(r, 0, self.R - 1, c)

    # O(1) -- max of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def maxGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(r, c, self.R - 1, self.C - 1)

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.mx[0][0][r * self.C + c]
