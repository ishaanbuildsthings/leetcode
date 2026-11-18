# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/compressed-difference-array/template.py
# @operations: getAll rectAdd
# @data-structure-type: difference-array
# @input: compressed
# @complexities:
#   getAll: X*Y
#   rectAdd: 1
#   build: X*Y
# @memory:
#   layout: none
#   node: diff[1*X*Y]
#   tags: none
#   other: base[1*X*Y] xs[1*X] ys[1*Y] xAt[1*X] yAt[1*Y]
#   note: X = how many distinct x's, Y = distinct y's; diff is (R + 1) by (C + 1), flat: each rectAdd writes its four corners



# 2D difference array: rectangle adds in O(1) each, then one O(R * C) pass (getAll) that turns them into the final
# grid. For when every update comes before any read: there are no queries in between (a Fenwick tree does rectAdd with
# pointGet in between at O(log R * log C) each). An add of v on rows r1..r2, columns c1..c2 marks +v at (r1, c1) and
# (r2 + 1, c2 + 1), and -v at (r1, c2 + 1) and (r2 + 1, c1); the 2D prefix sum of the marks is what every cell gained.
# Rows and columns are 0-based and rectangles are inclusive.
class DifferenceArray2D:
    __slots__ = ("R", "C", "W", "base", "diff")

    # O(R*C) -- grid: R rows of C numbers each (the starting values); needs R >= 1 and C >= 1, else ValueError
    def __init__(self, grid):
        R = self.R = len(grid)
        C = self.C = len(grid[0]) if R else 0
        if R < 1 or C < 1 or any(len(row) != C for row in grid):
            raise ValueError("DifferenceArray2D: needs a grid of R >= 1 rows, each of the same C >= 1 values")
        self.W = C + 1
        self.base = [list(row) for row in grid]
        self.diff = [0] * ((R + 1) * (C + 1))

    # O(1) -- adds v to every cell of rows r1..r2, columns c1..c2; needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, else
    # IndexError
    def rectAdd(self, r1, c1, r2, c2, v):
        if not (0 <= r1 <= r2 < self.R and 0 <= c1 <= c2 < self.C):
            raise IndexError(f"rectAdd: needs 0 <= r1 <= r2 < R and 0 <= c1 <= c2 < C, got r1 = {r1}, c1 = {c1}, "
                             f"r2 = {r2}, c2 = {c2}, R = {self.R}, C = {self.C}")
        diff, W = self.diff, self.W
        diff[r1 * W + c1] += v
        diff[r1 * W + c2 + 1] -= v
        diff[(r2 + 1) * W + c1] -= v
        diff[(r2 + 1) * W + c2 + 1] += v

    # O(R*C) -- the whole grid as it stands (R rows of C values); more rectAdd calls can follow
    def getAll(self):
        R, C, W, diff = self.R, self.C, self.W, self.diff
        out = []
        above = [0] * C
        for r in range(R):
            run = 0
            at = r * W
            row = self.base[r]
            cur = []
            for c in range(C):
                run += diff[at + c]
                cur.append(above[c] + run)
            above = cur
            out.append([cur[c] + row[c] for c in range(C)])
        return out


from bisect import bisect_left, bisect_right


# Coordinate compression in front of DifferenceArray2D: coordinates can be any integers (huge, negative, ...). You
# list every x and every y a point operation (pointGet, pointAdd, ...) will use; rectangles and corners can be any
# integers. Each listed x becomes a row and each listed y a column of a small grid, and the template above does the
# work on it. X = how many distinct x's, Y = distinct y's: memory and costs are the template's for an X by Y grid. A
# cell is a listed x with a listed y, and it is one point, not a block: a rectangle covers just the cells inside it
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
        self.ds = DifferenceArray2D([[0] * len(self.ys) for _ in self.xs])

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

    # O(X * Y) -- the whole grid, X rows of Y values: row i is the i-th smallest x, column j the j-th smallest y
    def getAll(self):
        return self.ds.getAll()

    # O(1) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2, else
    # IndexError; no cell inside: nothing happens
    def rectAdd(self, x1, y1, x2, y2, v):
        r = self._rect(x1, y1, x2, y2, "rectAdd")
        if r is not None:
            self.ds.rectAdd(*r, v)
