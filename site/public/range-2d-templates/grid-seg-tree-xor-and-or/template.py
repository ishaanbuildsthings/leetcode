# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-seg-tree-xor-and-or/template.py
# @operations: andAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectOr rectXor xorAll
# @data-structure-type: seg-tree
# @input: grid
# @complexities:
#   andAll: 1
#   orAll: 1
#   pointAdd: log(R)*log(C)
#   pointAssign: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   pointChmin: log(R)*log(C)
#   pointGet: 1
#   rectAnd: log(R)*log(C)
#   rectOr: log(R)*log(C)
#   rectXor: log(R)*log(C)
#   xorAll: 1
#   build: R*C
# @memory:
#   layout: 2n-iterative
#   node: xr[4*R*C] an[4*R*C] orr[4*R*C]
#   tags: none
#   other: none
#   note: one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries


# 2D segment tree (xor, AND, OR): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A
# tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class SegTree2D:
    __slots__ = ("R", "C", "W", "xr", "an", "orr")

    # O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        xr = self.xr = [0] * (2 * R * W)
        an = self.an = [0] * (2 * R * W)
        orr = self.orr = [0] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                xr[i] = v
                an[i] = v
                orr[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1]
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
                orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1]
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc]
                an[base + pc] = an[lo + pc] & an[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        xr, an, orr = self.xr, self.an, self.orr
        base = (r + R) * W
        i = base + c + C
        xr[i] = v
        an[i] = v
        orr[i] = v
        pc = (c + C) >> 1
        while pc:
            xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1]
            an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
            orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1]
            pc >>= 1
        pr = (r + R) >> 1
        while pr:
            base = pr * W
            lo = 2 * base
            hi = lo + W
            pc = c + C
            while pc:
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc]
                an[base + pc] = an[lo + pc] & an[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.xr[(r + self.R) * self.W + c + self.C]

    # O(log R * log C) -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c < C,
    # else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._set(r, c, v)

    # O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointAdd(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAdd: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.xr[(r + self.R) * self.W + c + self.C]
        self._set(r, c, cur + v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.xr[(r + self.R) * self.W + c + self.C]
        if v > cur:
            self._set(r, c, v)

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.xr[(r + self.R) * self.W + c + self.C]
        if v < cur:
            self._set(r, c, v)

    def _xorOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        xr = self.xr
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
                        res ^= xr[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res ^= xr[base + rc]
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
                        res ^= xr[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res ^= xr[base + rc]
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return res

    # O(log R * log C) -- xor of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectXor(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._xorOf(r1, c1, r2, c2)

    # O(1) -- xor of the whole grid
    def xorAll(self):
        return self.xr[self.W + 1]

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

    def _orOf(self, r1, c1, r2, c2):
        R, C, W = self.R, self.C, self.W
        orr = self.orr
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
                        res |= orr[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res |= orr[base + rc]
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
                        res |= orr[base + lc]
                        lc += 1
                    if rc & 1:
                        rc -= 1
                        res |= orr[base + rc]
                    lc >>= 1
                    rc >>= 1
            lr >>= 1
            rr >>= 1
        return res

    # O(log R * log C) -- OR of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectOr(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._orOf(r1, c1, r2, c2)

    # O(1) -- OR of the whole grid
    def orAll(self):
        return self.orr[self.W + 1]
