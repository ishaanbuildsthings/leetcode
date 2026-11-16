# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-max-gcd-and/template.py
# @operations: andAll gcdAll maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectGcd rectMax
# @data-structure-type: seg-tree
# @input: grid
# @empty-cells: yes
# @complexities:
#   andAll: 1
#   gcdAll: 1
#   maxAll: 1
#   maxGteGte: log(R)*log(C)
#   maxGteLte: log(R)*log(C)
#   maxLteGte: log(R)*log(C)
#   maxLteLte: log(R)*log(C)
#   pointAdd: log(R)*log(C)*log(U) ?
#   pointAssign: log(R)*log(C)*log(U) ?
#   pointChmax: log(R)*log(C)*log(U) ?
#   pointChmin: log(R)*log(C)*log(U) ?
#   pointGet: 1
#   rectAnd: log(R)*log(C)
#   rectGcd: log(R)*log(C)+log(U) ?
#   rectMax: log(R)*log(C)
#   build: R*C*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: mx[4*R*C] gc[4*R*C] an[4*R*C]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

from math import gcd

NEG = float("-inf")  # an empty cell in the max array


# 2D segment tree (max, gcd, AND): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A
# tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be empty (None in the
# grid) and queries only see set cells: a min / max over no set cell is None; a gcd over none is 0; an AND over none
# is -1 (every bit set).
class SegTree2D:
    __slots__ = ("R", "C", "W", "mx", "gc", "an")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        mx = self.mx = [NEG] * (2 * R * W)
        gc = self.gc = [0] * (2 * R * W)
        an = self.an = [-1] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                if v is not None:
                    mx[i] = v
                    gc[i] = v
                    an[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                lhs = mx[base + 2 * pc]
                rhs = mx[base + 2 * pc + 1]
                mx[base + pc] = lhs if lhs > rhs else rhs
                gc[base + pc] = gcd(gc[base + 2 * pc], gc[base + 2 * pc + 1])
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                lhs = mx[lo + pc]
                rhs = mx[hi + pc]
                mx[base + pc] = lhs if lhs > rhs else rhs
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])
                an[base + pc] = an[lo + pc] & an[hi + pc]

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        mx, gc, an = self.mx, self.gc, self.an
        base = (r + R) * W
        i = base + c + C
        mx[i] = v
        gc[i] = v
        an[i] = v
        pc = (c + C) >> 1
        while pc:
            lhs = mx[base + 2 * pc]
            rhs = mx[base + 2 * pc + 1]
            mx[base + pc] = lhs if lhs > rhs else rhs
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
                lhs = mx[lo + pc]
                rhs = mx[hi + pc]
                mx[base + pc] = lhs if lhs > rhs else rhs
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])
                an[base + pc] = an[lo + pc] & an[hi + pc]
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c), None if the cell is empty; needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mx[(r + self.R) * self.W + c + self.C]
        return None if cur == NEG else cur

    # O(log R * log C) gcds -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <=
    # c < C, else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._set(r, c, v)

    # O(log R * log C) gcds -- adds v to the cell at (r, c); an empty cell becomes v; needs 0 <= r < R and 0 <= c < C,
    # else IndexError
    def pointAdd(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAdd: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mx[(r + self.R) * self.W + c + self.C]
        self._set(r, c, v if cur == NEG else cur + v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mx[(r + self.R) * self.W + c + self.C]
        if cur == NEG or v > cur:
            self._set(r, c, v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mx[(r + self.R) * self.W + c + self.C]
        if cur == NEG or v < cur:
            self._set(r, c, v)

    def _maxOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        mx = self.mx
        res = NEG
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
                        cand = mx[base + lc]
                        if cand > res:
                            res = cand
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        cand = mx[base + rc]
                        if cand > res:
                            res = cand
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
                        cand = mx[base + lc]
                        if cand > res:
                            res = cand
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        cand = mx[base + rc]
                        if cand > res:
                            res = cand
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return None if res == NEG else res

    # O(log R * log C) -- max of the set cells in rows r1..r2, columns c1..c2 (None if there are none); needs 0 <= r1 <=
    # r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectMax(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectMax: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._maxOf(r1, c1, r2, c2)

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        res = self.mx[self.W + 1]
        return None if res == NEG else res

    # O(log R * log C) -- max of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(0, 0, r, c)

    # O(log R * log C) -- max of the set cells with row <= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(0, c, r, self.C - 1)

    # O(log R * log C) -- max of the set cells with row >= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(r, 0, self.R - 1, c)

    # O(log R * log C) -- max of the set cells with row >= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def maxGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"maxGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._maxOf(r, c, self.R - 1, self.C - 1)

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

    # O(log R * log C + log U) -- gcd of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0
    # <= r1
    # <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectGcd(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectGcd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._gcdOf(r1, c1, r2, c2)

    # O(1) -- gcd of every set cell (0 if there are none)
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

    # O(log R * log C) -- AND of the set cells in rows r1..r2, columns c1..c2 (-1 (every bit set) if there are none);
    # needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectAnd(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAnd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._andOf(r1, c1, r2, c2)

    # O(1) -- AND of every set cell (-1 (every bit set) if there are none)
    def andAll(self):
        return self.an[self.W + 1]
