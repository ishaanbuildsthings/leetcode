# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-sum-xor/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectSum rectXor sumAll xorAll
# @data-structure-type: BIT
# @input: grid
# @complexities:
#   pointAdd: log(R)*log(C)
#   pointAssign: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   pointChmin: log(R)*log(C)
#   pointGet: 1
#   rectSum: log(R)*log(C)
#   rectXor: log(R)*log(C)
#   sumAll: 1
#   xorAll: 1
#   build: R*C
# @memory:
#   layout: none
#   node: sm[1*R*C] xr[1*R*C]
#   tags: none
#   other: vals[1*R*C]
#   note: each Fenwick tree is (R + 1) by (C + 1), flat, 1-based; vals keeps the cells themselves for O(1) reads



# 2D Fenwick tree (sum and xor): point updates and any-rectangle sum and xor on an R x C grid, O(log R * log C) each,
# with a quarter of a 2D segment tree's memory and a smaller constant. A rectangle is four prefix queries (the big
# corner, minus the strip above, minus the strip to the left, plus the corner both took off). Rows and columns are
# 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class Fenwick2D:
    __slots__ = ("R", "C", "W", "vals", "sm", "xr", "totalSum", "totalXor")

    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("Fenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        vals = self.vals = [v for row in grid for v in row]
        t = self.sm = [0] * ((R + 1) * W)
        total = 0
        for v in vals:
            total += v
        for r in range(R):
            at = (r + 1) * W
            t[at + 1:at + W] = grid[r]
            for c in range(1, C + 1):  # each entry is added into the next one that covers it
                j = c + (c & -c)
                if j <= C:
                    t[at + j] += t[at + c]
        for r in range(1, R + 1):
            j = r + (r & -r)
            if j <= R:
                a = r * W
                b = j * W
                for c in range(1, C + 1):
                    t[b + c] += t[a + c]
        self.totalSum = total
        t = self.xr = [0] * ((R + 1) * W)
        total = 0
        for v in vals:
            total ^= v
        for r in range(R):
            at = (r + 1) * W
            t[at + 1:at + W] = grid[r]
            for c in range(1, C + 1):  # each entry is added into the next one that covers it
                j = c + (c & -c)
                if j <= C:
                    t[at + j] ^= t[at + c]
        for r in range(1, R + 1):
            j = r + (r & -r)
            if j <= R:
                a = r * W
                b = j * W
                for c in range(1, C + 1):
                    t[b + c] ^= t[a + c]
        self.totalXor = total

    # cell (r, c) becomes v
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        old = self.vals[r * C + c]
        self.vals[r * C + c] = v
        d = v - old
        self.totalSum += d
        t = self.sm
        i = r + 1
        while i <= R:
            base = i * W
            j = c + 1
            while j <= C:
                t[base + j] += d
                j += j & -j
            i += i & -i
        d = v ^ old
        self.totalXor ^= d
        t = self.xr
        i = r + 1
        while i <= R:
            base = i * W
            j = c + 1
            while j <= C:
                t[base + j] ^= d
                j += j & -j
            i += i & -i

    # sum of the first r rows and first c columns
    def _prefixSum(self, r, c):
        W, t, res = self.W, self.sm, 0
        while r > 0:
            base = r * W
            j = c
            while j > 0:
                res += t[base + j]
                j &= j - 1
            r &= r - 1
        return res

    # xor of the first r rows and first c columns
    def _prefixXor(self, r, c):
        W, t, res = self.W, self.xr, 0
        while r > 0:
            base = r * W
            j = c
            while j > 0:
                res ^= t[base + j]
                j &= j - 1
            r &= r - 1
        return res

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.vals[r * self.C + c]

    # O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else IndexError
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
        self._set(r, c, self.vals[r * self.C + c] + v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        if v > self.vals[r * self.C + c]:
            self._set(r, c, v)

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        if v < self.vals[r * self.C + c]:
            self._set(r, c, v)

    # O(log R * log C) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectSum(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        p = self._prefixSum
        return p(r2 + 1, c2 + 1) - p(r1, c2 + 1) - p(r2 + 1, c1) + p(r1, c1)

    # O(1) -- sum of the whole grid
    def sumAll(self):
        return self.totalSum

    # O(log R * log C) -- xor of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectXor(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        p = self._prefixXor
        return p(r2 + 1, c2 + 1) ^ p(r1, c2 + 1) ^ p(r2 + 1, c1) ^ p(r1, c1)

    # O(1) -- xor of the whole grid
    def xorAll(self):
        return self.totalXor
