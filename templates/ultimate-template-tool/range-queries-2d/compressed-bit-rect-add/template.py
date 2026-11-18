# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-bit-rect-add/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectAdd
# @data-structure-type: BIT
# @input: compressed
# @complexities:
#   pointAdd: log(X)*log(Y)
#   pointAssign: log(X)*log(Y)
#   pointChmax: log(X)*log(Y)
#   pointChmin: log(X)*log(Y)
#   pointGet: log(X)*log(Y)
#   rectAdd: log(X)*log(Y)
#   build: X*Y
# @memory:
#   layout: none
#   node: bit[1*X*Y]
#   tags: none
#   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
#   note: X = how many distinct x's, Y = distinct y's; one Fenwick tree over the marks a rectangle add leaves at its four corners; each is (R + 1) by (C + 1), flat



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


from bisect import bisect_left, bisect_right


# Coordinate compression in front of RectAddFenwick2D: coordinates can be any integers (huge, negative, ...). You list
# every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any integers.
# Each listed x becomes a row and each listed y a column of a small grid, and the template above does the work on it.
# X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A cell is a
# listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it
# (the gaps between listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you
# never set count as 0, a listed x with a listed y you never use together included.
class Compressed2D:
    __slots__ = ("xs", "ys", "xAt", "yAt", "ds")

    # O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use (any order, repeats are
    # fine), or an int n to leave x uncompressed as 0..n-1; ys: the same for y. Every cell starts at 0. Needs at least
    # one x and one y, else ValueError
    def __init__(self, xs, ys):
        self.xs = range(xs) if isinstance(xs, int) else sorted(set(xs))
        self.ys = range(ys) if isinstance(ys, int) else sorted(set(ys))
        if not self.xs or not self.ys:
            raise ValueError("Compressed2D: needs at least one x and one y")
        # a listed coordinate's row / column (None: that axis is 0..n-1 as it is)
        self.xAt = None if isinstance(xs, int) else {x: i for i, x in enumerate(self.xs)}
        self.yAt = None if isinstance(ys, int) else {y: i for i, y in enumerate(self.ys)}
        self.ds = RectAddFenwick2D([[0] * len(self.ys) for _ in self.xs])

    def _x(self, x, name):
        at = self.xAt
        if at is None:
            if 0 <= x < len(self.xs):
                return x
        elif x in at:
            return at[x]
        raise IndexError(f"{name}: x = {x} is not one of the xs given to the constructor")

    def _y(self, y, name):
        at = self.yAt
        if at is None:
            if 0 <= y < len(self.ys):
                return y
        elif y in at:
            return at[y]
        raise IndexError(f"{name}: y = {y} is not one of the ys given to the constructor")

    # the row and column of the cell (x, y)
    def _cell(self, x, y, name):
        return self._x(x, name), self._y(y, name)

    # the rows and columns a rectangle covers, (r1, c1, r2, c2); None when no listed x or no listed y is inside
    def _rect(self, x1, y1, x2, y2, name):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"{name}: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        r1, r2 = bisect_left(self.xs, x1), bisect_right(self.xs, x2) - 1
        c1, c2 = bisect_left(self.ys, y1), bisect_right(self.ys, y2) - 1
        if r1 > r2 or c1 > c2:
            return None
        return r1, c1, r2, c2

    # O(log X * log Y) -- adds v to the cell (x, y); x must be one of the xs and y one of the ys, else IndexError
    def pointAdd(self, x, y, v):
        return self.ds.pointAdd(*self._cell(x, y, "pointAdd"), v)

    # O(log X * log Y) -- the cell (x, y) becomes v; x must be one of the xs and y one of the ys, else IndexError
    def pointAssign(self, x, y, v):
        return self.ds.pointAssign(*self._cell(x, y, "pointAssign"), v)

    # O(log X * log Y) -- the cell (x, y) becomes max(itself, v); x must be one of the xs and y one of the ys, else
    # IndexError
    def pointChmax(self, x, y, v):
        return self.ds.pointChmax(*self._cell(x, y, "pointChmax"), v)

    # O(log X * log Y) -- the cell (x, y) becomes min(itself, v); x must be one of the xs and y one of the ys, else
    # IndexError
    def pointChmin(self, x, y, v):
        return self.ds.pointChmin(*self._cell(x, y, "pointChmin"), v)

    # O(log X * log Y) -- the value at (x, y); x must be one of the xs and y one of the ys, else IndexError
    def pointGet(self, x, y):
        return self.ds.pointGet(*self._cell(x, y, "pointGet"))

    # O(log X * log Y) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1
    # <= y2, else IndexError; no cell inside: nothing happens
    def rectAdd(self, x1, y1, x2, y2, v):
        r = self._rect(x1, y1, x2, y2, "rectAdd")
        if r is not None:
            self.ds.rectAdd(*r, v)
