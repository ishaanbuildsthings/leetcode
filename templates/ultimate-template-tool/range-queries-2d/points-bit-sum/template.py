# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-sum/template.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
# @data-structure-type: BIT
# @input: points
# @complexities:
#   pointAdd: log^2(N)
#   pointAssign: log^2(N)
#   pointChmax: log^2(N)
#   pointChmin: log^2(N)
#   pointGet: log(N)
#   rectSum: log^2(N)
#   sumAll: 1
#   sumGteGte: log^2(N)
#   sumGteLte: log^2(N)
#   sumLteGte: log^2(N)
#   sumLteLte: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sm[1*N*log(N)]
#   tags: none
#   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[1*N] cnt[1*N]
#   note: every point's y is listed in each of the O(log N) Fenwick x-nodes covering it; an x-node's own Fenwick tree is as long as its list

from bisect import bisect_left, bisect_right


# 2D Fenwick tree over a fixed list of points (sum): point updates and any-rectangle sum in O(log^2 N), with N log N
# memory whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y) your point
# operations will use (rectangles take any integers, never listed); every point starts at 0. A Fenwick tree over the
# distinct x's; every node of it keeps the sorted y's of the points it covers and a Fenwick tree over just those. Half
# the memory of the segment tree version and a smaller constant, for sum only. Rectangles are inclusive, x1..x2 by
# y1..y2, and their corners can be any integers, given or not.
class PointsFenwick2D:
    __slots__ = ("n", "pts", "vals", "xs", "ys", "off", "cnt", "sm", "totalSum")

    # O(N log N) -- points: every (x, y) a point operation (pointGet, pointAdd, ...) will use, as pairs of integers
    # (negative is fine, repeats are fine); not rectangle or corner coordinates, those can be anything. Needs at least
    # one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsFenwick2D: needs at least one point")
        pts = self.pts = sorted(set(map(tuple, points)))
        self.vals = [0] * len(pts)
        xs = self.xs = sorted({x for x, _ in pts})
        n = self.n = len(xs)
        lists = [[] for _ in range(n + 1)]  # per Fenwick x-node: the distinct y's it covers, ascending
        for x, y in sorted(pts, key=lambda p: p[1]):
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
        self.sm = [0] * len(ys)  # x-node i's own Fenwick tree is [off[i], off[i] + cnt[i]), 1-based inside
        self.totalSum = 0

    # where (x, y) is in the sorted points
    def _index(self, x, y, name):
        pts = self.pts
        i = bisect_left(pts, (x, y))
        if i == len(pts) or pts[i] != (x, y):
            raise IndexError(f"{name}: ({x}, {y}) is not one of the points given to the constructor")
        return i

    # point number i, at (x, y), becomes v
    def _set(self, i, x, y, v):
        old = self.vals[i]
        self.vals[i] = v
        xs, ys, off, cnt, n = self.xs, self.ys, self.off, self.cnt, self.n
        d = v - old
        self.totalSum += d
        t = self.sm
        i = bisect_left(xs, x) + 1
        while i <= n:
            o = off[i]
            c = cnt[i]
            k = bisect_left(ys, y, o, o + c) - o + 1
            o -= 1
            while k <= c:
                t[o + k] += d
                k += k & -k
            i += i & -i

    # sum of the points with x <= the given x and y <= the given y
    def _prefixSum(self, x, y):
        xs, ys, off, cnt, t = self.xs, self.ys, self.off, self.cnt, self.sm
        res = 0
        i = bisect_right(xs, x)
        while i > 0:
            o = off[i]
            k = bisect_right(ys, y, o, o + cnt[i]) - o
            o -= 1
            while k > 0:
                res += t[o + k]
                k &= k - 1
            i &= i - 1
        return res

    # O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointGet(self, x, y):
        return self.vals[self._index(x, y, "pointGet")]

    # O(log^2 N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else IndexError
    def pointAssign(self, x, y, v):
        i = self._index(x, y, "pointAssign")
        self._set(i, x, y, v)

    # O(log^2 N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointAdd(self, x, y, v):
        i = self._index(x, y, "pointAdd")
        self._set(i, x, y, self.vals[i] + v)

    # O(log^2 N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmax(self, x, y, v):
        i = self._index(x, y, "pointChmax")
        if v > self.vals[i]:
            self._set(i, x, y, v)

    # O(log^2 N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmin(self, x, y, v):
        i = self._index(x, y, "pointChmin")
        if v < self.vals[i]:
            self._set(i, x, y, v)

    # O(log^2 N) -- sum of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2 and
    # y1 <= y2, else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        p = self._prefixSum
        return p(x2, y2) - p(x1 - 1, y2) - p(x2, y1 - 1) + p(x1 - 1, y1 - 1)

    # O(1) -- sum of every point
    def sumAll(self):
        return self.totalSum

    # O(log^2 N) -- sum of the points with x <= the given x and y <= the given y (0 if there are none); any integers
    def sumLteLte(self, x, y):
        p = self._prefixSum
        INF = float("inf")
        return p(x, y)

    # O(log^2 N) -- sum of the points with x <= the given x and y >= the given y (0 if there are none); any integers
    def sumLteGte(self, x, y):
        p = self._prefixSum
        INF = float("inf")
        return p(x, INF) - p(x, y - 1)

    # O(log^2 N) -- sum of the points with x >= the given x and y <= the given y (0 if there are none); any integers
    def sumGteLte(self, x, y):
        p = self._prefixSum
        INF = float("inf")
        return p(INF, y) - p(x - 1, y)

    # O(log^2 N) -- sum of the points with x >= the given x and y >= the given y (0 if there are none); any integers
    def sumGteGte(self, x, y):
        p = self._prefixSum
        INF = float("inf")
        return self.totalSum - p(x - 1, INF) - p(INF, y - 1) + p(x - 1, y - 1)
