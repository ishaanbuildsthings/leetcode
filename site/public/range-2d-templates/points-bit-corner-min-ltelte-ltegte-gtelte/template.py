# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-bit-corner-min-ltelte-ltegte-gtelte/template.py
# @operations: minAll minGteLte minLteGte minLteLte pointChmin
# @data-structure-type: BIT
# @input: points
# @empty-cells: yes
# @complexities:
#   minAll: 1
#   minGteLte: log^2(N)
#   minLteGte: log^2(N)
#   minLteLte: log^2(N)
#   pointChmin: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: tree[3*N*log(N)]
#   tags: none
#   other: ys[3*N*log(N)] xs[3*N] off[3*N] cnt[3*N] pts[2*N]
#   note: one Fenwick-of-Fenwicks per corner direction asked for (a >= direction is the same structure on negated coordinates)

from bisect import bisect_left, bisect_right

POS = float("inf")  # a point never set


# min over the points with x <= a given x and y <= a given y, values only going down
class _PrefixMinFenwick:
    __slots__ = ("n", "xs", "ys", "off", "cnt", "tree")

    def __init__(self, pts):
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
        self.tree = [POS] * len(ys)

    def improve(self, x, y, v):
        xs, ys, off, cnt, t, n = self.xs, self.ys, self.off, self.cnt, self.tree, self.n
        i = bisect_left(xs, x) + 1
        while i <= n:
            o = off[i]
            c = cnt[i]
            k = bisect_left(ys, y, o, o + c) - o + 1
            o -= 1
            while k <= c:
                if v < t[o + k]:
                    t[o + k] = v
                k += k & -k
            i += i & -i

    def best(self, x, y):
        xs, ys, off, cnt, t = self.xs, self.ys, self.off, self.cnt, self.tree
        res = POS
        i = bisect_right(xs, x)
        while i > 0:
            o = off[i]
            k = bisect_right(ys, y, o, o + cnt[i]) - o
            o -= 1
            while k > 0:
                z = t[o + k]
                if z < res:
                    res = z
                k &= k - 1
            i &= i - 1
        return res


# Corner min over points known up front, with Fenwick trees: pointChmin at a point and the min over a corner of the
# plane (every point with x <= or >= a given x, and y <= or >= a given y) in O(log^2 N), with N log N memory per
# direction whatever the coordinates are (any integers, negative is fine). The constructor takes every (x, y) that
# will ever be updated. This works because values only move one way: a point can only go down, so a tree entry never
# has to forget a value; for a point that can move both ways, or for rectangles that aren't corners, use the segment
# tree version. Every point starts empty and queries only see points that have been set. A min over no set point is
# None.
class PointsCornerMinFenwick2D:
    __slots__ = ("pts", "top", "tLteLte", "tLteGte", "tGteLte")

    # O(N log N) -- points: every (x, y) that will ever be updated, as pairs of integers (negative is fine, repeats are
    # fine); needs at least one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsCornerMinFenwick2D: needs at least one point")
        pts = self.pts = sorted(set(map(tuple, points)))
        self.top = POS
        self.tLteLte = _PrefixMinFenwick(pts)
        self.tLteGte = _PrefixMinFenwick(sorted((x, -y) for x, y in pts))
        self.tGteLte = _PrefixMinFenwick(sorted((-x, y) for x, y in pts))

    # O(log^2 N) -- the point (x, y) becomes min(itself, v); an empty point becomes v; needs (x, y) to be one of the
    # points given, else IndexError
    def pointChmin(self, x, y, v):
        pts = self.pts
        i = bisect_left(pts, (x, y))
        if i == len(pts) or pts[i] != (x, y):
            raise IndexError(f"pointChmin: ({x}, {y}) is not one of the points given to the constructor")
        if v < self.top:
            self.top = v
        self.tLteLte.improve(x, y, v)
        self.tLteGte.improve(x, -y, v)
        self.tGteLte.improve(-x, y, v)

    # O(log^2 N) -- min of the set points with x <= the given x and y <= the given y (None if there are none); any
    # integers
    def minLteLte(self, x, y):
        res = self.tLteLte.best(x, y)
        return None if res == POS else res

    # O(log^2 N) -- min of the set points with x <= the given x and y >= the given y (None if there are none); any
    # integers
    def minLteGte(self, x, y):
        res = self.tLteGte.best(x, -y)
        return None if res == POS else res

    # O(log^2 N) -- min of the set points with x >= the given x and y <= the given y (None if there are none); any
    # integers
    def minGteLte(self, x, y):
        res = self.tGteLte.best(-x, y)
        return None if res == POS else res

    # O(1) -- min of every set point (None if there are none)
    def minAll(self):
        return None if self.top == POS else self.top
