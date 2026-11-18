# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-seg-tree-and-or/template.py
# @operations: andAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectOr
# @data-structure-type: seg-tree
# @input: compressed
# @complexities:
#   andAll: 1
#   orAll: 1
#   pointAdd: log(X)*log(Y)
#   pointAssign: log(X)*log(Y)
#   pointChmax: log(X)*log(Y)
#   pointChmin: log(X)*log(Y)
#   pointGet: 1
#   rectAnd: log(X)*log(Y)
#   rectOr: log(X)*log(Y)
#   build: X*Y
# @memory:
#   layout: 2n-iterative
#   node: an[4*X*Y] orr[4*X*Y]
#   tags: none
#   other: xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
#   note: X = how many distinct x's, Y = distinct y's; one flat array per aggregate, 2R row-nodes by 2C column-nodes; the cells are the last R row-nodes' last C entries


# 2D segment tree (AND, OR): point updates and any-rectangle queries on an R x C grid, O(log R * log C) each. A tree
# over the rows whose every node is a tree over the columns, bottom-up, in one flat array per aggregate. Rows and
# columns are 0-based and rectangles are inclusive: rows r1..r2, columns c1..c2.
class SegTree2D:
    __slots__ = ("R", "C", "W", "an", "orr")

    # O(R*C) -- grid: R rows of C values each; needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("SegTree2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        W = self.W = 2 * C
        an = self.an = [0] * (2 * R * W)
        orr = self.orr = [0] * (2 * R * W)
        for r in range(R):
            base = (r + R) * W
            i = base + C
            for v in grid[r]:
                an[i] = v
                orr[i] = v
                i += 1
            for pc in range(C - 1, 0, -1):
                an[base + pc] = an[base + 2 * pc] & an[base + 2 * pc + 1]
                orr[base + pc] = orr[base + 2 * pc] | orr[base + 2 * pc + 1]
        for pr in range(R - 1, 0, -1):
            base = pr * W
            lo = 2 * base
            hi = lo + W
            for pc in range(1, W):
                an[base + pc] = an[lo + pc] & an[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]

    # cell (r, c) = v, then every node above it
    def _set(self, r, c, v):
        R, C, W = self.R, self.C, self.W
        an, orr = self.an, self.orr
        base = (r + R) * W
        i = base + c + C
        an[i] = v
        orr[i] = v
        pc = (c + C) >> 1
        while pc:
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
                an[base + pc] = an[lo + pc] & an[hi + pc]
                orr[base + pc] = orr[lo + pc] | orr[hi + pc]
                pc >>= 1
            pr >>= 1

    # O(1) -- the value at (r, c); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointGet(self, r, c):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointGet: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        return self.orr[(r + self.R) * self.W + c + self.C]

    # O(log R * log C) -- the cell at (r, c) becomes v (it may go down as well as up); needs 0 <= r < R and 0 <= c <
    # C, else IndexError
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
        cur = self.orr[(r + self.R) * self.W + c + self.C]
        self._set(r, c, cur + v)

    # O(log R * log C) -- the cell at (r, c) becomes max(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmax(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmax: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.orr[(r + self.R) * self.W + c + self.C]
        if v > cur:
            self._set(r, c, v)

    # O(log R * log C) -- the cell at (r, c) becomes min(itself, v); needs 0 <= r < R and 0 <= c < C, else IndexError
    def pointChmin(self, r, c, v):
        if not (0 <= r < self.R and 0 <= c < self.C):
            raise IndexError(f"pointChmin: needs 0 <= r < R and 0 <= c < C, got r = {r}, c = {c}, R = {self.R}, "
                             f"C = {self.C}")
        cur = self.orr[(r + self.R) * self.W + c + self.C]
        if v < cur:
            self._set(r, c, v)

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



from bisect import bisect_left, bisect_right


# Coordinate compression in front of SegTree2D: coordinates can be any integers (huge, negative, ...). You list every
# x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any integers. Each
# listed x becomes a row and each listed y a column of a small grid, and the template above does the work on it. X =
# how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A cell is a listed
# x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it (the gaps between
# listed coordinates don't exist), so a sum adds those cells' values, it is not an area. Cells you never set count as
# 0, a listed x with a listed y you never use together included.
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
        self.ds = SegTree2D([[0] * len(self.ys) for _ in self.xs])

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

    # O(1) -- AND of every cell
    def andAll(self):
        return self.ds.andAll()

    # O(1) -- OR of every cell
    def orAll(self):
        return self.ds.orAll()

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

    # O(1) -- the value at (x, y); x must be one of the xs and y one of the ys, else IndexError
    def pointGet(self, x, y):
        return self.ds.pointGet(*self._cell(x, y, "pointGet"))

    # O(log X * log Y) -- AND of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    # y2, else IndexError; IndexError if no cell is inside
    def rectAnd(self, x1, y1, x2, y2):
        r = self._rect(x1, y1, x2, y2, "rectAnd")
        if r is None:
            raise IndexError("rectAnd: no cell is inside the rectangle")
        return self.ds.rectAnd(*r)

    # O(log X * log Y) -- OR of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <=
    # y2, else IndexError; 0 if no cell is inside
    def rectOr(self, x1, y1, x2, y2):
        r = self._rect(x1, y1, x2, y2, "rectOr")
        if r is None:
            return 0
        return self.ds.rectOr(*r)
