# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-seg-tree-min-xor-or/template.py
# @operations: minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectMin rectOr rectXor xorAll
# @data-structure-type: seg-tree
# @input: compressed
# @empty-cells: yes
# @complexities:
#   minAll: 1
#   minGteGte: log(X)*log(Y)
#   minGteLte: log(X)*log(Y)
#   minLteGte: log(X)*log(Y)
#   minLteLte: log(X)*log(Y)
#   orAll: 1
#   pointAdd: log(X)*log(Y)
#   pointAssign: log(X)*log(Y)
#   pointChmax: log(X)*log(Y)
#   pointChmin: log(X)*log(Y)
#   pointGet: 1
#   rectMin: log(X)*log(Y)
#   rectOr: log(X)*log(Y)
#   rectXor: log(X)*log(Y)
#   xorAll: 1
#   build: X*Y
# @memory:
#   layout: 2n-iterative
#   node: mn[4*X*Y] xr[4*X*Y] orr[4*X*Y]
#   tags: none
#   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
#   note: X = how many distinct x's, Y = distinct y's; one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries

POS = float("inf")  # an empty cell in the min array


# 2D segment tree (min, xor, OR): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A
# tree over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2. A cell can be empty (None in the
# grid) and queries only see set cells: a min / max over no set cell is None; a xor / OR over none is 0.
class SegTree2D:
    __slots__ = ("R", "C", "W", "mn", "xr", "orr")

    # O(R*C) -- grid: R rows of C values each (None = an empty cell); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        mn = self.mn = [POS] * (2 * R * W)
        xr = self.xr = [0] * (2 * R * W)
        orr = self.orr = [0] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                if v is not None:
                    mn[i] = v
                    xr[i] = v
                    orr[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                lhs = mn[base + 2 * pc]
                rhs = mn[base + 2 * pc + 1]
                mn[base + pc] = lhs if lhs < rhs else rhs
                xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1]
                orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1]
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                lhs = mn[lo + pc]
                rhs = mn[hi + pc]
                mn[base + pc] = lhs if lhs < rhs else rhs
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        mn, xr, orr = self.mn, self.xr, self.orr
        base = (r + R) * W
        i = base + c + C
        mn[i] = v
        xr[i] = v
        orr[i] = v
        pc = (c + C) >> 1
        while pc:
            lhs = mn[base + 2 * pc]
            rhs = mn[base + 2 * pc + 1]
            mn[base + pc] = lhs if lhs < rhs else rhs
            xr[base + pc] = xr[base + 2 * pc] ^ xr[base + 2 * pc + 1]
            orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1]
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
                xr[base + pc] = xr[lo + pc] ^ xr[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c), None if the cell is empty; needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        return None if cur == POS else cur

    # O(log R * log C) -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c <
    # C, else IndexError
    def pointAssign(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAssign: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        self._set(r, c, v)

    # O(log R * log C) -- adds v to the cell at (r, c); an empty cell becomes v; needs 0 <= r < R and 0 <= c < C, else
    # IndexError
    def pointAdd(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointAdd: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        self._set(r, c, v if cur == POS else cur + v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.mn[(r + self.R) * self.W + c + self.C]
        if cur == POS or v > cur:
            self._set(r, c, v)

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); an empty cell becomes v; needs 0 <= r < R and 0
    # <= c < C, else IndexError
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

    # O(log R * log C) -- xor of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <= r1 <=
    # r2 <
    # R and 0 <= c1 <= c2 < C, else IndexError
    def rectXor(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectXor: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._xorOf(r1, c1, r2, c2)

    # O(1) -- xor of every set cell (0 if there are none)
    def xorAll(self):
        return self.xr[self.W + 1]

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

    # O(log R * log C) -- OR of the set cells in rows r1..r2, columns c1..c2 (0 if there are none); needs 0 <= r1 <=
    # r2 <
    # R and 0 <= c1 <= c2 < C, else IndexError
    def rectOr(self, r1, c1, r2, c2):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectOr: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        return self._orOf(r1, c1, r2, c2)

    # O(1) -- OR of every set cell (0 if there are none)
    def orAll(self):
        return self.orr[self.W + 1]



from bisect import bisect_left, bisect_right


# Coordinate compression in front of SegTree2D: coordinates can be any integers (huge, negative, ...). You list every
# x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any integers. Each
# listed x becomes a row and each listed y a column of a small grid, and the template above does the work on it. X =
# how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A cell is a listed
# x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it (the gaps between
# listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you never set count as
# empty, a listed x with a listed y you never use together included.
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
        self.ds = SegTree2D([[None] * len(self.ys) for _ in self.xs])

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

    # O(log X * log Y) -- min of the cells with x >= the given x and y <= the given y (None if there are none); any
    # integers; None if no cell is there
    def minGteLte(self, x, y):
        r = self._corner(x, y, "Gte", "Lte")
        if r is None:
            return None
        return self.ds.minGteLte(*r)

    # O(log X * log Y) -- min of the cells with x <= the given x and y >= the given y (None if there are none); any
    # integers; None if no cell is there
    def minLteGte(self, x, y):
        r = self._corner(x, y, "Lte", "Gte")
        if r is None:
            return None
        return self.ds.minLteGte(*r)

    # O(log X * log Y) -- min of the cells with x <= the given x and y <= the given y (None if there are none); any
    # integers; None if no cell is there
    def minLteLte(self, x, y):
        r = self._corner(x, y, "Lte", "Lte")
        if r is None:
            return None
        return self.ds.minLteLte(*r)

    # O(1) -- OR of every cell
    def orAll(self):
        return self.ds.orAll()

    # O(log X * log Y) -- adds v to the cell (x, y); an empty cell becomes v; x must be one of the xs and y one of the
    # ys, else IndexError
    def pointAdd(self, x, y, v):
        return self.ds.pointAdd(*self._cell(x, y, "pointAdd"), v)

    # O(log X * log Y) -- the cell (x, y) becomes v; an empty cell becomes v; x must be one of the xs and y one of the
    # ys, else IndexError
    def pointAssign(self, x, y, v):
        return self.ds.pointAssign(*self._cell(x, y, "pointAssign"), v)

    # O(log X * log Y) -- the cell (x, y) becomes max(itself, v); an empty cell becomes v; x must be one of the xs and y
    # one of the ys, else IndexError
    def pointChmax(self, x, y, v):
        return self.ds.pointChmax(*self._cell(x, y, "pointChmax"), v)

    # O(log X * log Y) -- the cell (x, y) becomes min(itself, v); an empty cell becomes v; x must be one of the xs and y
    # one of the ys, else IndexError
    def pointChmin(self, x, y, v):
        return self.ds.pointChmin(*self._cell(x, y, "pointChmin"), v)

    # O(1) -- the value at (x, y), None if the cell is empty; x must be one of the xs and y one of the ys, else
    # IndexError
    def pointGet(self, x, y):
        return self.ds.pointGet(*self._cell(x, y, "pointGet"))

    # O(log X * log Y) -- min of the cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); any integers,
    # needs x1 <= x2 and y1 <= y2, else IndexError; None if no cell is inside
    def rectMin(self, x1, y1, x2, y2):
        r = self._rect(x1, y1, x2, y2, "rectMin")
        if r is None:
            return None
        return self.ds.rectMin(*r)

    # O(log X * log Y) -- OR of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    # y2, else IndexError; 0 if no cell is inside
    def rectOr(self, x1, y1, x2, y2):
        r = self._rect(x1, y1, x2, y2, "rectOr")
        if r is None:
            return 0
        return self.ds.rectOr(*r)

    # O(log X * log Y) -- XOR of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    # y2, else IndexError; 0 if no cell is inside
    def rectXor(self, x1, y1, x2, y2):
        r = self._rect(x1, y1, x2, y2, "rectXor")
        if r is None:
            return 0
        return self.ds.rectXor(*r)

    # O(1) -- XOR of every cell
    def xorAll(self):
        return self.ds.xorAll()
