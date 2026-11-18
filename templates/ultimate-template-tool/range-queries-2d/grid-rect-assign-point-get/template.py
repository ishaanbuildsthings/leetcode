# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-rect-assign-point-get/template.py
# @operations: pointAssign pointGet rectAssign
# @data-structure-type: seg-tree-kept-tags
# @input: grid
# @complexities:
#   pointAssign: log(R)*log(C)
#   pointGet: log(R)*log(C)
#   rectAssign: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: 2n-iterative
#   node: stamp[4*R*C]
#   tags: none
#   other: vals[1*R*C]
#   note: 2R row-nodes by 2C column-nodes of timestamps, flat; vals holds the grid's values then one more per write (the value written at each timestamp)

# Rectangle assign and point get on an R x C grid, O(log R * log C) each. rectAssign(r1, c1, r2, c2, v) makes every
# cell of the rectangle v; pointGet(r, c) reads one cell. Every write gets the next timestamp, and a 2D segment tree
# keeps the newest timestamp at the nodes that make up the write's rectangle (no push-down: a newer write always wins,
# so nothing is ever undone). A read takes the newest timestamp on its cell's path up both trees and returns the value
# written at that time. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. For
# rectangle sums or maxes after rectangle assigns, there is no log^2 template: loop the rows with a 1D lazy segment
# tree each.
class RectAssignPointGet2D:
    __slots__ = ("R", "C", "W", "stamp", "vals")

    # O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("RectAssignPointGet2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        stamp = self.stamp = [0] * (2 * R * W)
        vals = self.vals = [None]  # vals[t]: the value written at timestamp t; 1..R*C are the grid's own
        for r in range(R):
            base = (r + R) * W + C
            for c in range(C):
                vals.append(grid[r][c])
                stamp[base + c] = len(vals) - 1

    # one column tree (the one starting at `base`): columns c1..c2 get timestamp t
    def _mark(self, base, c1, c2, t):
        stamp = self.stamp
        lo = c1 + self.C
        hi = c2 + self.C + 1
        while lo < hi:
            if lo & 1:
                stamp[base + lo] = t
                lo += 1
            if hi & 1:
                hi -= 1
                stamp[base + hi] = t
            lo >>= 1
            hi >>= 1

    # every cell of the rectangle gets the next timestamp, which stands for v
    def _write(self, r1, c1, r2, c2, v):
        self.vals.append(v)
        t = len(self.vals) - 1
        W = self.W
        lo = r1 + self.R
        hi = r2 + self.R + 1
        while lo < hi:
            if lo & 1:
                self._mark(lo * W, c1, c2, t)
                lo += 1
            if hi & 1:
                hi -= 1
                self._mark(hi * W, c1, c2, t)
            lo >>= 1
            hi >>= 1

    # O(log R * log C) -- every cell of rows r1..r2, columns c1..c2 becomes v; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2
    # < C, else IndexError
    def rectAssign(self, r1, c1, r2, c2, v):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAssign: needs 0 <= r1 <= r2 < R = {self.R} and 0 <= c1 <= c2 < C = {self.C}, "
                             f"got r1 = {r1}, c1 = {c1}, r2 = {r2}, c2 = {c2}")
        self._write(r1, c1, r2, c2, v)

    # O(log R * log C) -- the cell (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R = {self.R} and 0 <= c < C = {self.C}, "
                             f"got r = {r}, c = {c}")
        self._write(r, c, r, c, v)

    # O(log R * log C) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        R, C, W, stamp = self.R, self.C, self.W, self.stamp
        if not (0 <= r < R and 0 <= c < C):
            raise IndexError(f"pointGet: needs 0 <= r < R = {R} and 0 <= c < C = {C}, got r = {r}, c = {c}")
        best = 0
        pr = r + R
        while pr:
            base = pr * W
            pc = c + C
            while pc:
                s = stamp[base + pc]
                if s > best:
                    best = s
                pc >>= 1
            pr >>= 1
        return self.vals[best]
