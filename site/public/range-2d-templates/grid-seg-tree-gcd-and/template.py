# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-gcd-and/template.py
# @operations: andAll gcdAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectGcd
# @data-structure-type: seg-tree
# @input: grid
# @complexities:
#   andAll: 1
#   gcdAll: 1
#   pointAdd: log(R)*log(C)*log(U) ?
#   pointAssign: log(R)*log(C)*log(U) ?
#   pointChmax: log(R)*log(C)*log(U) ?
#   pointChmin: log(R)*log(C)*log(U) ?
#   pointGet: 1
#   rectAnd: log(R)*log(C)
#   rectGcd: log(R)*log(C)+log(U) ?
#   build: R*C*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: gc[4*R*C] an[4*R*C]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

from math import gcd


# 2D segment tree (gcd, AND): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A tree
# over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class SegTree2D:
    __slots__ = ("R", "C", "W", "gc", "an")

    # O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        gc = self.gc = [0] * (2 * R * W)
        an = self.an = [0] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                gc[i] = v
                an[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                gc[base + pc] = gcd(gc[base + 2 * pc], gc[base + 2 * pc + 1])
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])
                an[base + pc] = an[lo + pc] & an[hi + pc]

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        gc, an = self.gc, self.an
        base = (r + R) * W
        i = base + c + C
        gc[i] = v
        an[i] = v
        pc = (c + C) >> 1
        while pc:
            gc[base + pc] = gcd(gc[base + 2 * pc], gc[base + 2 * pc + 1])
            an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
            pc >>= 1
        pr = (r + R) >> 1
        while pr:
            base = pr * W
            lo = 2 * base
            hi = lo + W
            pc = c + C
            while pc:
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])
                an[base + pc] = an[lo + pc] & an[hi + pc]
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.gc[(r + self.R) * self.W + c + self.C]

    # O(log R * log C) gcds -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c
    # < C, else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._set(r, c, v)

    # O(log R * log C) gcds -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointAdd(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAdd: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.gc[(r + self.R) * self.W + c + self.C]
        self._set(r, c, cur + v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.gc[(r + self.R) * self.W + c + self.C]
        if v > cur:
            self._set(r, c, v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.gc[(r + self.R) * self.W + c + self.C]
        if v < cur:
            self._set(r, c, v)

    def _gcdOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        gc = self.gc
        res = 0
        lr = r1 + R
        rr = r2 + R + 1
        cl = c1 + C
        cr = c2 + C + 1
        while lr < rr:
            if lr & 1:
                base = lr * W
                lc = cl
                rc = cr
                while lc < rc:
                    if lc & 1:
                        res = gcd(res, gc[base + lc])
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res = gcd(res, gc[base + rc])
                    lc >>= 1
                    rc >>= 1
                lr += 1
            if rr & 1:
                rr -= 1
                base = rr * W
                lc = cl
                rc = cr
                while lc < rc:
                    if lc & 1:
                        res = gcd(res, gc[base + lc])
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res = gcd(res, gc[base + rc])
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return res

    # O(log R * log C + log U) -- gcd of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C,
    # else IndexError
    def rectGcd(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectGcd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._gcdOf(r1, c1, r2, c2)

    # O(1) -- gcd of the whole grid
    def gcdAll(self):
        return abs(self.gc[self.W + 1])

    def _andOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        an = self.an
        res = -1
        lr = r1 + R
        rr = r2 + R + 1
        cl = c1 + C
        cr = c2 + C + 1
        while lr < rr:
            if lr & 1:
                base = lr * W
                lc = cl
                rc = cr
                while lc < rc:
                    if lc & 1:
                        res &= an[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res &= an[base + rc]
                    lc >>= 1
                    rc >>= 1
                lr += 1
            if rr & 1:
                rr -= 1
                base = rr * W
                lc = cl
                rc = cr
                while lc < rc:
                    if lc & 1:
                        res &= an[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res &= an[base + rc]
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return res

    # O(log R * log C) -- AND of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectAnd(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAnd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._andOf(r1, c1, r2, c2)

    # O(1) -- AND of the whole grid
    def andAll(self):
        return self.an[self.W + 1]
