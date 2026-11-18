# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-rect-add/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd
# @data-structure-type: BIT
# @input: grid
# @complexities:
#   pointAdd: log(R)*log(C)
#   pointAssign: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   pointChmin: log(R)*log(C)
#   pointGet: log(R)*log(C)
#   rectAdd: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: none
#   node: bit[1*R*C]
#   tags: none
#   other: none
#   note: one Fenwick tree over the marks a rectangle add leaves at its four corners; each is (R + 1) by (C + 1), flat



# Rectangle add and point read on an R x C grid with one 2D Fenwick tree, O(log R * log C) each. An add of v on rows
# r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + 1), -v at (r1, c2 + 1) and (r2 + 1, c1);
# a cell's value is the sum of the marks above-left of it, a prefix query. When every add comes before any read, the
# difference array does this in O(1) per add. Rows and columns are 0-based and rectangles are inclusive.
class RectAddFenwick2D:
    __slots__ = ("R", "C", "W", "bit")

    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("RectAddFenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        bit = self.bit = [0] * ((R + 1) * W)
        above = [0] * C
        for r in range(R):
            row = grid[r]
            at = (r + 1) * W
            left = 0
            aboveLeft = 0
            for c in range(C):
                d = row[c] - left - above[c] + aboveLeft  # the mark that makes this cell's value come out right
                left = row[c]
                aboveLeft = above[c]
                bit[at + c + 1] = d
            above = row
        for t in (bit,):
            for r in range(1, R + 1):
                at = r * W
                for c in range(1, C + 1):
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

    # a mark d at (r, c): every cell at or below-right of it gains d
    def _mark(self, r, c, d):
        R, C, W, bit = self.R, self.C, self.W, self.bit
        i = r + 1
        while i <= R:
            base = i * W
            j = c + 1
            while j <= C:
                bit[base + j] += d
                j += j & -j
            i += i & -i

    def _add(self, r1, c1, r2, c2, v):
        self._mark(r1, c1, v)
        if c2 + 1 < self.C:
            self._mark(r1, c2 + 1, -v)
        if r2 + 1 < self.R:
            self._mark(r2 + 1, c1, -v)
            if c2 + 1 < self.C:
                self._mark(r2 + 1, c2 + 1, v)

    def _get(self, r, c):
        W, bit, res = self.W, self.bit, 0
        i = r + 1
        while i > 0:
            base = i * W
            j = c + 1
            while j > 0:
                res += bit[base + j]
                j &= j - 1
            i &= i - 1
        return res

    # O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2
    # < C, else IndexError
    def rectAdd(self, r1, c1, r2, c2, v):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        self._add(r1, c1, r2, c2, v)

    # O(log R * log C) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self._get(r, c)

    # O(log R * log C) -- the cell at (r, c) becomes v; needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._add(r, c, r, c, v - self._get(r, c))

    # O(log R * log C) -- adds v to the cell at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointAdd(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAdd: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._add(r, c, r, c, v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self._get(r, c)
        if v > cur:
            self._add(r, c, r, c, v - cur)

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self._get(r, c)
        if v < cur:
            self._add(r, c, r, c, v - cur)
