# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-prefix-sum/template.py
# @operations: pointGet rectSum sumAll
# @data-structure-type: prefix-sum
# @input: grid
# @complexities:
#   pointGet: 1
#   rectSum: 1
#   sumAll: 1
#   build: R*C
# @memory:
#   layout: none
#   node: sm[1*R*C]
#   tags: none
#   other: none
#   note: each table is (R + 1) by (C + 1), flat: entry [r][c] covers the rows above r and the columns left of c



# Static 2D prefix sums: any rectangle in O(1) from four table entries (the big corner, minus the strip above, minus
# the strip to the left, plus the corner both took off). No updates. Rows and columns are 0-based and rectangles are
# inclusive: rows r1..r2, columns c1..c2.
class PrefixSums2D:
    __slots__ = ("R", "C", "W", "sm")

    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("PrefixSums2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        sm = self.sm = [0] * ((R + 1) * W)
        for r in range(R):
            row = grid[r]
            up = r * W
            at = up + W
            runSum = 0
            for c in range(C):
                runSum += row[c]
                sm[at + c + 1] = sm[up + c + 1] + runSum

    # O(1) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectSum(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        sm, W = self.sm, self.W
        top = r1 * W
        bot = (r2 + 1) * W
        return sm[bot + c2 + 1] - sm[top + c2 + 1] - sm[bot + c1] + sm[top + c1]

    # O(1) -- sum of the whole grid
    def sumAll(self):
        return self.sm[-1]

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        sm, W = self.sm, self.W
        top = r * W
        bot = top + W
        return sm[bot + c + 1] - sm[top + c + 1] - sm[bot + c] + sm[top + c]
