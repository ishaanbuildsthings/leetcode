# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-bit-corner-min-ltelte-gtegte/template.py
# @operations: minAll minGteGte minLteLte pointChmin
# @data-structure-type: BIT
# @input: compressed
# @empty-cells: yes
# @complexities:
#   minAll: 1
#   minGteGte: log(X)*log(Y)
#   minLteLte: log(X)*log(Y)
#   pointChmin: log(X)*log(Y)
#   build: X*Y
# @memory:
#   layout: none
#   node: tLteLte[1*X*Y] tGteGte[1*X*Y]
#   tags: none
#   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
#   note: X = how many distinct x's, Y = distinct y's; one Fenwick tree per corner direction, each (R + 1) by (C + 1), flat; a >= direction is the same tree with that axis mirrored

POS = float("inf")  # an empty cell


# Corner min with a 2D Fenwick tree: pointChmin at a cell and the min over a corner of the grid (every cell with row
# <= r or >= r, and column <= c or >= c), O(log R * log C) each, with a quarter of a 2D segment tree's memory per
# direction and a much smaller constant. This works because values only move one way: a cell can only go down
# (pointChmin), so a tree entry never has to forget a value. For a cell that can move both ways, or for rectangles
# that aren't corners, use the 2D segment tree. A cell can be empty and queries only see set cells. Rows and columns
# are 0-based. An empty cell is None in the grid, and a min over no set cell is None.
class CornerMinFenwick2D:
    __slots__ = ("R", "C", "W", "best", "tLteLte", "tGteGte")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("CornerMinFenwick2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = C + 1
        best = POS
        t = self.tLteLte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (r + 1) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + c + 1] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        t = self.tGteGte = [POS] * ((R + 1) * W)
        for r in range(R):
            at = (R - r) * W
            row = grid[r]
            for c in range(C):
                v = row[c]
                if v is not None:
                    t[at + C - c] = v
                    if v < best:
                        best = v
        for i in range(1, R + 1):
            at = i * W
            for j in range(1, C + 1):  # each entry is folded into the next one that covers it
                p = j + (j & -j)
                if p <= C and t[at + j] < t[at + p]:
                    t[at + p] = t[at + j]
        for i in range(1, R + 1):
            p = i + (i & -i)
            if p <= R:
                a = i * W
                b = p * W
                for j in range(1, C + 1):
                    if t[a + j] < t[b + j]:
                        t[b + j] = t[a + j]
        self.best = best

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        R, C, W = self.R, self.C, self.W
        if v < self.best:
            self.best = v
        t = self.tLteLte
        i = r + 1
        cj = c + 1
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v < t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i
        t = self.tGteGte
        i = R - r
        cj = C - c
        while i <= R:
            base = i * W
            j = cj
            while j <= C:
                if v < t[base + j]:
                    t[base + j] = v
                j += j & -j
            i += i & -i

    # O(log R * log C) -- min of the set cells with row <= r and column <= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minLteLte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minLteLte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tLteLte, POS
        i = r + 1
        cj = c + 1
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(log R * log C) -- min of the set cells with row >= r and column >= c (None if there are none); needs 0 <= r < R
    # and 0 <= c < C, else IndexError
    def minGteGte(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"minGteGte: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        W, t, res = self.W, self.tGteGte, POS
        i = self.R - r
        cj = self.C - c
        while i > 0:
            base = i * W
            j = cj
            while j > 0:
                x = t[base + j]
                if x < res:
                    res = x
                j &= j - 1
            i &= i - 1
        return None if res == POS else res

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        return None if self.best == POS else self.best


from bisect import bisect_left, bisect_right


# Coordinate compression in front of CornerMinFenwick2D: coordinates can be any integers (huge, negative, ...). You
# list every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any
# integers. Each listed x becomes a row and each listed y a column of a small grid, and the template above does the
# work on it. X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A
# cell is a listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it
# (the gaps between listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you
# never set count as empty, a listed x with a listed y you never use together included.
class Compressed2D:
    __slots__ = ("xs", "ys", "xAt", "yAt", "ds")

    # O(X log X + Y log Y + the template's build) -- xs: every x a point operation will use (any order, repeats are
    # fine), or an int n to leave x uncompressed as 0..n-1; ys: the same for y. Every cell starts empty. Needs at least
    # one x and one y, else ValueError
    def __init__(self, xs, ys):
        self.xs = range(xs) if isinstance(xs, int) else sorted(set(xs))
        self.ys = range(ys) if isinstance(ys, int) else sorted(set(ys))
        if not self.xs or not self.ys:
            raise ValueError("Compressed2D: needs at least one x and one y")
        # a listed coordinate's row / column (None: that axis is 0..n-1 as it is)
        self.xAt = None if isinstance(xs, int) else {x: i for i, x in enumerate(self.xs)}
        self.yAt = None if isinstance(ys, int) else {y: i for i, y in enumerate(self.ys)}
        self.ds = CornerMinFenwick2D([[None] * len(self.ys) for _ in self.xs])

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

    # the cell a corner query starts from: the last listed x <= x (Lte) or the first listed x >= x (Gte), the same for
    # y; None when there is none
    def _corner(self, x, y, xSide, ySide):
        r = bisect_right(self.xs, x) - 1 if xSide == "Lte" else bisect_left(self.xs, x)
        c = bisect_right(self.ys, y) - 1 if ySide == "Lte" else bisect_left(self.ys, y)
        if not (0 <= r < len(self.xs) and 0 <= c < len(self.ys)):
            return None
        return r, c

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        return self.ds.minAll()

    # O(log X * log Y) -- min of the cells with x >= the given x and y >= the given y (None if there are none); any
    # integers; None if no cell is there
    def minGteGte(self, x, y):
        r = self._corner(x, y, "Gte", "Gte")
        if r is None:
            return None
        return self.ds.minGteGte(*r)

    # O(log X * log Y) -- min of the cells with x <= the given x and y <= the given y (None if there are none); any
    # integers; None if no cell is there
    def minLteLte(self, x, y):
        r = self._corner(x, y, "Lte", "Lte")
        if r is None:
            return None
        return self.ds.minLteLte(*r)

    # O(log X * log Y) -- the cell (x, y) becomes min(itself, v); an empty cell becomes v; x must be one of the xs and y
    # one of the ys, else IndexError
    def pointChmin(self, x, y, v):
        return self.ds.pointChmin(*self._cell(x, y, "pointChmin"), v)
