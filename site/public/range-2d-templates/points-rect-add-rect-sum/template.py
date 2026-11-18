# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-rect-add-rect-sum/template.py
# @operations: pointAdd pointGet rectAdd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
# @data-structure-type: BIT
# @input: points
# @model: area
# @complexities:
#   pointAdd: log^2(N)
#   pointGet: log^2(N)
#   rectAdd: log^2(N)
#   rectSum: log^2(N)
#   sumAll: 1
#   sumGteGte: log^2(N)
#   sumGteLte: log^2(N)
#   sumLteGte: log^2(N)
#   sumLteLte: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: s0[4*N*log(N)] sx[4*N*log(N)] sy[4*N*log(N)] sxy[4*N*log(N)]
#   tags: none
#   other: ys[4*N*log(N)] xs[4*N] off[4*N] cnt[4*N] rects[4*N]
#   note: N = how many rectangles; each makes four corner marks, and every mark's y is listed in each of the O(log N) Fenwick x-nodes covering it


from bisect import bisect_left, bisect_right


# Rectangle add and rectangle sum where the update rectangles are listed up front, any integers (negative is fine):
# O(log^2 N) per operation with N log N memory, N = how many rectangles. A rect add is four point marks at its corners
# (+v, -v, -v, +v), and the sum of the cells with x <= X and y <= Y comes from four sums over the marks below and left
# of (X, Y): of d, d * x, d * y and d * x * y. Those are point updates at known places, so a Fenwick tree over the
# marks' x's whose every node is a Fenwick tree over just its own y's keeps them. The constructor takes every rectangle
# a rectAdd will use (a pointAdd is the rectangle (x, y, x, y)); queries take any integers, never listed.
# Every cell starts at 0, and sums are true area sums: a rect add of v on a 3 by 4 rectangle adds 12 * v.
class PointsRectAddRectSum2D:
    __slots__ = ("rects", "xs", "ys", "off", "cnt", "s0", "sx", "sy", "sxy", "maxX", "maxY", "total")

    # O(N log N) -- rects: every (x1, y1, x2, y2) a rectAdd will use, x1 <= x2 and y1 <= y2 (a pointAdd at (x, y) needs
    # (x, y, x, y)); repeats are fine; queries are never listed. Needs at least one, else ValueError
    def __init__(self, rects):
        rects = self.rects = set(map(tuple, rects))
        if not rects:
            raise ValueError("PointsRectAddRectSum2D: needs at least one rectangle")
        if any(x1 > x2 or y1 > y2 for x1, y1, x2, y2 in rects):
            raise ValueError("PointsRectAddRectSum2D: needs x1 <= x2 and y1 <= y2 in every rectangle")
        marks = set()
        for x1, y1, x2, y2 in rects:
            marks.update(((x1, y1), (x2 + 1, y1), (x1, y2 + 1), (x2 + 1, y2 + 1)))
        xs = self.xs = sorted({x for x, _ in marks})
        n = len(xs)
        self.maxX = xs[-1]  # (past the last mark, a prefix sum stops changing)
        self.maxY = max(y for _, y in marks)
        lists = [[] for _ in range(n + 1)]  # per Fenwick x-node: the distinct y's it covers, ascending
        for x, y in sorted(marks, key=lambda m: m[1]):
            i = bisect_left(xs, x) + 1
            while i <= n:
                lst = lists[i]
                if not lst or lst[-1] != y:
                    lst.append(y)
                i += i & -i
        off = self.off = [0] * (n + 1)
        cnt = self.cnt = [0] * (n + 1)
        ys = self.ys = []
        for i in range(1, n + 1):
            off[i] = len(ys)
            cnt[i] = len(lists[i])
            ys += lists[i]
        self.s0 = [0] * len(ys)  # the sums of d, d * x, d * y, d * x * y, Fenwick-style per x-node
        self.sx = [0] * len(ys)
        self.sy = [0] * len(ys)
        self.sxy = [0] * len(ys)
        self.total = 0

    def _mark(self, x, y, d):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        s0, sx, sy, sxy = self.s0, self.sx, self.sy, self.sxy
        dx = d * x
        dy = d * y
        dxy = dx * y
        n = len(xs)
        i = bisect_left(xs, x) + 1
        while i <= n:
            o = off[i]
            c = cnt[i]
            k = bisect_left(ys, y, o, o + c) - o + 1
            o -= 1
            while k <= c:
                s0[o + k] += d
                sx[o + k] += dx
                sy[o + k] += dy
                sxy[o + k] += dxy
                k += k & -k
            i += i & -i

    # the sum of the cells with x <= X and y <= Y (any integers)
    def _prefix(self, X, Y):
        if X > self.maxX:
            X = self.maxX
        if Y > self.maxY:
            Y = self.maxY
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        s0, sx, sy, sxy = self.s0, self.sx, self.sy, self.sxy
        a = b = c = e = 0
        i = bisect_right(xs, X)
        while i > 0:
            o = off[i]
            k = bisect_right(ys, Y, o, o + cnt[i]) - o
            o -= 1
            while k > 0:
                a += s0[o + k]
                b += sx[o + k]
                c += sy[o + k]
                e += sxy[o + k]
                k &= k - 1
            i &= i - 1
        return (X + 1) * (Y + 1) * a - (Y + 1) * b - (X + 1) * c + e

    def _add(self, x1, y1, x2, y2, v, name):
        if (x1, y1, x2, y2) not in self.rects:
            raise IndexError(f"{name}: ({x1}, {y1}, {x2}, {y2}) is not one of the rectangles given to the constructor")
        self.total += v * (x2 - x1 + 1) * (y2 - y1 + 1)
        self._mark(x1, y1, v)
        self._mark(x2 + 1, y1, -v)
        self._mark(x1, y2 + 1, -v)
        self._mark(x2 + 1, y2 + 1, v)

    def _sum(self, x1, y1, x2, y2):
        return self._prefix(x2, y2) - self._prefix(x1 - 1, y2) - self._prefix(x2, y1 - 1) + self._prefix(x1 - 1, y1 - 1)

    # O(log^2 N) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs (x1, y1, x2, y2) to be one of the
    # rectangles given, else IndexError
    def rectAdd(self, x1, y1, x2, y2, v):
        self._add(x1, y1, x2, y2, v, "rectAdd")

    # O(log^2 N) -- adds v to the cell (x, y); needs (x, y, x, y) to be one of the rectangles given, else IndexError
    def pointAdd(self, x, y, v):
        self._add(x, y, x, y, v, "pointAdd")

    # O(log^2 N) -- the value at (x, y); any integers
    def pointGet(self, x, y):
        return self._sum(x, y, x, y)

    # O(log^2 N) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; any integers, needs x1 <= x2 and y1 <= y2,
    # else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._sum(x1, y1, x2, y2)

    # O(1) -- sum of every cell
    def sumAll(self):
        return self.total

    # O(log^2 N) -- sum of the cells with x <= the given x and y <= the given y; any integers
    def sumLteLte(self, x, y):
        return self._prefix(x, y)

    # O(log^2 N) -- sum of the cells with x <= the given x and y >= the given y; any integers
    def sumLteGte(self, x, y):
        return self._prefix(x, self.maxY) - self._prefix(x, y - 1)

    # O(log^2 N) -- sum of the cells with x >= the given x and y <= the given y; any integers
    def sumGteLte(self, x, y):
        return self._prefix(self.maxX, y) - self._prefix(x - 1, y)

    # O(log^2 N) -- sum of the cells with x >= the given x and y >= the given y; any integers
    def sumGteGte(self, x, y):
        return self.total - self._prefix(x - 1, self.maxY) - self._prefix(self.maxX, y - 1) + self._prefix(x - 1, y - 1)
