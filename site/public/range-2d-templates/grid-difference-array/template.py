# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-difference-array/template.py
# @operations: getAll rectAdd
# @data-structure-type: difference-array
# @input: grid
# @complexities:
#   getAll: R*C
#   rectAdd: 1
#   build: R*C
# @memory:
#   layout: none
#   node: diff[1*R*C]
#   tags: none
#   other: base[1*R*C]
#   note: diff is (R + 1) by (C + 1), flat: each rectAdd writes its four corners



# 2D difference array: rectangle adds in O(1) each, then one O(R * C) pass (getAll) that turns them into the final
# grid. For when every update comes before any read: there are no queries in between (a Fenwick tree does rectAdd with
# pointGet in between at O(log R * log C) each). An add of v on rows r1..r2, columns c1..c2 marks +v at (r1, c1) and
# (r2 + 1, c2 + 1), and -v at (r1, c2 + 1) and (r2 + 1, c1); the 2D prefix sum of the marks is what every cell gained.
# Rows and columns are 0-based and rectangles are inclusive.
class DifferenceArray2D:
    __slots__ = ("R", "C", "W", "base", "diff")

    # O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("DifferenceArray2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        self.W = C + 1
        self.base = [list(row) for row in grid]
        self.diff = [0] * ((R + 1) * (C + 1))

    # O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectAdd(self, r1, c1, r2, c2, v):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        diff, W = self.diff, self.W
        diff[r1 * W + c1] += v
        diff[r1 * W + c2 + 1] -= v
        diff[(r2 + 1) * W + c1] -= v
        diff[(r2 + 1) * W + c2 + 1] += v

    # O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow
    def getAll(self):
        R, C, W, diff = self.R, self.C, self.W, self.diff
        out = []
        above = [0] * C
        for r in range(R):
            run = 0
            at = r * W
            row = self.base[r]
            cur = []
            for c in range(C):
                run += diff[at + c]
                cur.append(above[c] + run)
            above = cur
            out.append([cur[c] + row[c] for c in range(C)])
        return out
