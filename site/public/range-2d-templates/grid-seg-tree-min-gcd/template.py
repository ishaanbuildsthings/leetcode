# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-min-gcd/template.py
# @operations: gcdAll minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectMin
# @data-structure-type: seg-tree
# @input: grid
# @empty-cells: yes
# @complexities:
#   gcdAll: 1
#   minAll: 1
#   minGteGte: log(R)*log(C)
#   minGteLte: log(R)*log(C)
#   minLteGte: log(R)*log(C)
#   minLteLte: log(R)*log(C)
#   pointAdd: log(R)*log(C)*log(U) ?
#   pointAssign: log(R)*log(C)*log(U) ?
#   pointChmax: log(R)*log(C)*log(U) ?
#   pointChmin: log(R)*log(C)*log(U) ?
#   pointGet: 1
#   rectGcd: log(R)*log(C)+log(U) ?
#   rectMin: log(R)*log(C)
#   build: R*C*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: mn[4*R*C] gc[4*R*C]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

from math import gcd

POS = float("inf")  # an empty cell in the min array


# 2D segment tree (min, gcd): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A tree
# over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be empty (None in the
# grid) and queries only see set cells: a min / max over no set cell is None; a gcd over none is 0.
class SegTree2D:
    __slots__ = ("R", "C", "W", "mn", "gc")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        mn = self.mn = [POS] * (2 * R * W)
        gc = self.gc = [0] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                if v is not None:
                    mn[i] = v
                    gc[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                lhs = mn[base + 2 * pc]
                rhs = mn[base + 2 * pc + 1]
                mn[base + pc] = lhs if lhs < rhs else rhs
                gc[base + pc] = gcd(gc[base + 2 * pc], gc[base + 2 * pc + 1])
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                lhs = mn[lo + pc]
                rhs = mn[hi + pc]
                mn[base + pc] = lhs if lhs < rhs else rhs
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        mn, gc = self.mn, self.gc
        base = (r + R) * W
        i = base + c + C
        mn[i] = v
        gc[i] = v
        pc = (c + C) >> 1
        while pc:
            lhs = mn[base + 2 * pc]
            rhs = mn[base + 2 * pc + 1]
            mn[base + pc] = lhs if lhs < rhs else rhs
            gc[base + pc] = gcd(gc[base + 2 * pc], gc[base + 2 * pc + 1])
            pc >>= 1
        pr = (r + R) >> 1
        while pr:
            base = pr * W
            lo = 2 * base
            hi = lo + W
            pc = c + C
            while pc:
                lhs = mn[lo + pc]
                rhs = mn[hi + pc]
                mn[base + pc] = lhs if lhs < rhs else rhs
                gc[base + pc] = gcd(gc[lo + pc], gc[hi + pc])
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c), None if the cell is empty; needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        return None if cur == POS else cur

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
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        self._set(r, c, v if cur == POS else cur + v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        if cur == POS or v > cur:
            self._set(r, c, v)

    # O(log R * log C) gcds -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        if cur == POS or v < cur:
            self._set(r, c, v)

    def _minOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        mn = self.mn
        res = POS
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
                        cand = mn[base + lc]
                        if cand < res:
                            res = cand
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        cand = mn[base + rc]
                        if cand < res:
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
                        cand = mn[base + lc]
                        if cand < res:
                            res = cand
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        cand = mn[base + rc]
                        if cand < res:
                            res = cand
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells in rows r1..r2, columns c1..c2 (None if there are none); needs 0 <= r1 <=
    # r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectMin(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectMin: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._minOf(r1, c1, r2, c2)

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        res = self.mn[self.W + 1]
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(0, 0, r, c)

    # O(log R * log C) -- min of the set cells with row <= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(0, c, r, self.C - 1)

    # O(log R * log C) -- min of the set cells with row >= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(r, 0, self.R - 1, c)

    # O(log R * log C) -- min of the set cells with row >= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._minOf(r, c, self.R - 1, self.C - 1)

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
