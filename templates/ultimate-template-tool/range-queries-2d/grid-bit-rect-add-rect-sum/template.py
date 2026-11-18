# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/grid-bit-rect-add-rect-sum/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
# @data-structure-type: BIT
# @input: grid
# @complexities:
#   pointAdd: log(R)*log(C)
#   pointAssign: log(R)*log(C)
#   pointChmax: log(R)*log(C)
#   pointChmin: log(R)*log(C)
#   pointGet: log(R)*log(C)
#   rectAdd: log(R)*log(C)
#   rectSum: log(R)*log(C)
#   sumAll: 1
#   sumGteGte: log(R)*log(C)
#   sumGteLte: log(R)*log(C)
#   sumLteGte: log(R)*log(C)
#   sumLteLte: log(R)*log(C)
#   build: R*C
# @memory:
#   layout: none
#   node: b1[1*R*C] bx[1*R*C] by[1*R*C] bxy[1*R*C]
#   tags: none
#   other: none
#   note: four Fenwick trees over the marks a rectangle add leaves at its corners: the mark itself, times its row, times its column, times both; each is (R + 1) by (C + 1), flat



# Rectangle add and rectangle sum on an R x C grid with four 2D Fenwick trees, O(log R * log C) each, no lazy tags. An
# add of v on rows r1..r2, columns c1..c2 leaves four marks, +v at (r1, c1) and (r2 + 1, c2 + 1), -v at (r1, c2 + 1)
# and (r2 + 1, c1): a cell's value is the sum of the marks above-left of it. The sum of the first x rows and y columns
# is then, over the marks (i, j, d) above-left, the sum of d * (x - i) * (y - j), which splits into x*y * sum(d) - y *
# sum(d*i) - x * sum(d*j) + sum(d*i*j): one tree per sum. Rows and columns are 0-based and rectangles are inclusive.
class RectAddRectSumFenwick2D:
    __slots__ = ("R", "C", "W", "b1", "bx", "by", "bxy", "total")

    # O(R*C) -- grid: R rows of C numbers each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("RectAddRectSumFenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        b1 = self.b1 = [0] * ((R + 1) * W)
        bx = self.bx = [0] * ((R + 1) * W)
        by = self.by = [0] * ((R + 1) * W)
        bxy = self.bxy = [0] * ((R + 1) * W)
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
                b1[at + c + 1] = d
                bx[at + c + 1] = d * r
                by[at + c + 1] = d * c
                bxy[at + c + 1] = d * r * c
            above = row
        for t in (b1, bx, by, bxy):
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
        self.total = sum(v for row in grid for v in row)

    # a mark d at (r, c): every cell at or below-right of it gains d
    def _mark(self, r, c, d):
        R, C, W = self.R, self.C, self.W
        b1, bx, by, bxy = self.b1, self.bx, self.by, self.bxy
        dx = d * r
        dy = d * c
        dxy = dx * c
        i = r + 1
        while i <= R:
            base = i * W
            j = c + 1
            while j <= C:
                b1[base + j] += d
                bx[base + j] += dx
                by[base + j] += dy
                bxy[base + j] += dxy
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
        self.total += v * (r2 - r1 + 1) * (c2 - c1 + 1)

    # sum of the first x rows and first y columns
    def _prefix(self, x, y):
        W = self.W
        b1, bx, by, bxy = self.b1, self.bx, self.by, self.bxy
        s1 = sx = sy = sxy = 0
        i = x
        while i > 0:
            base = i * W
            j = y
            while j > 0:
                s1 += b1[base + j]
                sx += bx[base + j]
                sy += by[base + j]
                sxy += bxy[base + j]
                j &= j - 1
            i &= i - 1
        return x * y * s1 - y * sx - x * sy + sxy

    def _sumOf(self, r1, c1, r2, c2):
        p = self._prefix
        return p(r2 + 1, c2 + 1) - p(r1, c2 + 1) - p(r2 + 1, c1) + p(r1, c1)

    def _get(self, r, c):
        return self._sumOf(r, c, r, c)

    # O(log R * log C) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <=
    # c2 <
    # C, else IndexError
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

    # O(log R * log C) -- sum of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectSum(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectSum: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._sumOf(r1, c1, r2, c2)

    # O(1) -- sum of the whole grid
    def sumAll(self):
        return self.total

    # O(log R * log C) -- sum of the cells with row <= r and column <= c; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def sumLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"sumLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.rectSum(0, 0, r, c)

    # O(log R * log C) -- sum of the cells with row <= r and column >= c; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def sumLteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"sumLteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.rectSum(0, c, r, self.C - 1)

    # O(log R * log C) -- sum of the cells with row >= r and column <= c; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def sumGteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"sumGteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.rectSum(r, 0, self.R - 1, c)

    # O(log R * log C) -- sum of the cells with row >= r and column >= c; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def sumGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"sumGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.rectSum(r, c, self.R - 1, self.C - 1)
