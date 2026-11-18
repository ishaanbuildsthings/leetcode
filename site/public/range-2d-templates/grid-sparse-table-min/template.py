# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-sparse-table-min/template.py
# @operations: minAll minGteGte minGteLte minLteGte minLteLte pointGet rectMin
# @data-structure-type: sparse-table
# @input: grid
# @complexities:
#   minAll: 1
#   minGteGte: 1
#   minGteLte: 1
#   minLteGte: 1
#   minLteLte: 1
#   pointGet: 1
#   rectMin: 1
#   build: R*C*log(R)*log(C)
# @memory:
#   layout: none
#   node: mn[1*R*C*log(R)*log(C)]
#   tags: none
#   other: none
#   note: per aggregate, one table for every pair of a power-of-two height and a power-of-two width (the 1 x 1 table is the grid itself, shared)



# Static 2D sparse table (min): any rectangle in O(1). For every power-of-two height and power-of-two width there is a
# table holding the aggregate of each window of that size; a rectangle is covered by four such windows, one in each
# corner (they overlap, which is fine: each of these gives the same answer when a cell is counted twice). Memory and
# build are R * C * log R * log C. No updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2,
# columns c1..c2.
class SparseTable2D:
    __slots__ = ("R", "C", "mn")

    # O(R*C*logR*logC) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SparseTable2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        flat = [v for row in grid for v in row]
        levelsR = R.bit_length()
        levelsC = C.bit_length()
        t = self.mn = [[None] * levelsC for _ in range(levelsR)]  # t[kr][kc]: windows of 2^kr rows by 2^kc columns
        t[0][0] = flat
        for kc in range(1, levelsC):
            half = 1 << (kc - 1)
            prevW = C - half + 1
            prev = t[0][kc - 1]
            cur = []
            for r in range(R):
                seg = prev[r * prevW:(r + 1) * prevW]
                cur += [x if x < y else y for x, y in zip(seg, seg[half:])]
            t[0][kc] = cur
        for kr in range(1, levelsR):
            half = 1 << (kr - 1)
            for kc in range(levelsC):
                prev = t[kr - 1][kc]
                off = half * (C - (1 << kc) + 1)
                t[kr][kc] = [x if x < y else y for x, y in zip(prev, prev[off:])]

    def _minOf(self, r1, c1, r2, c2):
        kr = (r2 - r1 + 1).bit_length() - 1
        kc = (c2 - c1 + 1).bit_length() - 1
        t = self.mn[kr][kc]
        w = self.C - (1 << kc) + 1
        i = r1 * w + c1
        j = (r2 - (1 << kr) + 1) * w + c1
        d = c2 - (1 << kc) + 1 - c1
        return min(t[i], t[i + d], t[j], t[j + d])

    # O(1) -- min of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectMin(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._minOf(r1, c1, r2, c2)

    # O(1) -- min of the whole grid
    def minAll(self):
        return self._minOf(0, 0, self.R - 1, self.C - 1)

    # O(1) -- min of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def minLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(0, 0, r, c)

    # O(1) -- min of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def minLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(0, c, r, self.C - 1)

    # O(1) -- min of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def minGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(r, 0, self.R - 1, c)

    # O(1) -- min of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else IndexError
    def minGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(r, c, self.R - 1, self.C - 1)

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.mn[0][0][r * self.C + c]
