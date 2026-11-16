# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-counts-and-or/template.py
# @operations: andAll orAll pointGet rectAnd rectOr
# @data-structure-type: bit-counts
# @input: grid
# @values: non-negative
# @complexities:
#   andAll: log(U)
#   orAll: log(U)
#   pointGet: 1
#   rectAnd: log(U)
#   rectOr: log(U)
#   build: R*C*log(U)
# @memory:
#   layout: none
#   node: cnt[1*R*C*log(U)]
#   tags: none
#   other: vals[1*R*C]
#   note: one (R + 1) by (C + 1) prefix-count table per bit of the largest value



# Static rectangle AND and OR from one 2D prefix-count table per bit: a bit is in the OR when some cell of the
# rectangle has it, and in the AND when every cell does. O(bits) per query, bits = bit length of the largest value,
# and bits * R * C memory (a sparse table answers in O(1) but takes log R * log C tables). Values must be >= 0. No
# updates. Rows and columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class BitCounts2D:
    __slots__ = ("R", "C", "W", "bits", "cnt", "vals")

    # O(R*C*bits) -- grid: R rows of C numbers each, all >= 0; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("BitCounts2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        if any(v < 0 for row in grid for v in row):
            raise ValueError("BitCounts2D: values must be >= 0")
        W = self.W = C + 1
        self.vals = [v for row in grid for v in row]
        bits = self.bits = max(1, max(self.vals).bit_length())
        cnt = self.cnt = []
        for b in range(bits):
            t = [0] * ((R + 1) * W)
            for r in range(R):
                row = grid[r]
                up = r * W
                at = up + W
                run = 0
                for c in range(C):
                    run += row[c] >> b & 1
                    t[at + c + 1] = t[up + c + 1] + run
            cnt.append(t)

    # how many cells of the rectangle have each bit, one count per bit
    def _counts(self, r1, c1, r2, c2):
        W = self.W
        a = (r2 + 1) * W + c2 + 1
        b = r1 * W + c2 + 1
        c = (r2 + 1) * W + c1
        d = r1 * W + c1
        return [t[a] - t[b] - t[c] + t[d] for t in self.cnt]

    # O(bits) -- AND of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectAnd(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAnd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        area = (r2 - r1 + 1) * (c2 - c1 + 1)
        res = 0
        for b, n in enumerate(self._counts(r1, c1, r2, c2)):
            if n == area:
                res |= 1 << b
        return res

    # O(bits) -- AND of the whole grid
    def andAll(self):
        r1, c1, r2, c2 = 0, 0, self.R - 1, self.C - 1
        area = (r2 - r1 + 1) * (c2 - c1 + 1)
        res = 0
        for b, n in enumerate(self._counts(r1, c1, r2, c2)):
            if n == area:
                res |= 1 << b
        return res

    # O(bits) -- OR of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else IndexError
    def rectOr(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        res = 0
        for b, n in enumerate(self._counts(r1, c1, r2, c2)):
            if n:
                res |= 1 << b
        return res

    # O(bits) -- OR of the whole grid
    def orAll(self):
        r1, c1, r2, c2 = 0, 0, self.R - 1, self.C - 1
        res = 0
        for b, n in enumerate(self._counts(r1, c1, r2, c2)):
            if n:
                res |= 1 << b
        return res

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.vals[r * self.C + c]
