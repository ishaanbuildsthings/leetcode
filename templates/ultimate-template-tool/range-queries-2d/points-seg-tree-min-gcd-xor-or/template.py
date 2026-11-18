# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-seg-tree-min-gcd-xor-or/template.py
# @operations: gcdAll minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectMin rectOr rectXor xorAll
# @data-structure-type: seg-tree
# @input: points
# @empty-cells: yes
# @complexities:
#   gcdAll: 1
#   minAll: 1
#   minGteGte: log^2(N)
#   minGteLte: log^2(N)
#   minLteGte: log^2(N)
#   minLteLte: log^2(N)
#   orAll: 1
#   pointAdd: log^2(N)*log(U) ?
#   pointAssign: log^2(N)*log(U) ?
#   pointChmax: log^2(N)*log(U) ?
#   pointChmin: log^2(N)*log(U) ?
#   pointGet: log(N)
#   rectGcd: log^2(N)+log(U) ?
#   rectMin: log^2(N)
#   rectOr: log^2(N)
#   rectXor: log^2(N)
#   xorAll: 1
#   build: N*log(N)
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N*log(N)] gc[2*N*log(N)] xr[2*N*log(N)] orr[2*N*log(N)]
#   tags: none
#   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]
#   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list

from bisect import bisect_left, bisect_right
from math import gcd

NEG = float("-inf")  # an empty point in a max array; also "no lower bound" on a coordinate
POS = float("inf")  # an empty point in a min array; also "no upper bound" on a coordinate


# 2D segment tree over a fixed list of points (min, gcd, xor, OR): point updates and any-rectangle queries in O(log^2
# N), with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every
# (x, y) your point operations will use; rectangles and corners take any integers, never listed. A bottom-up tree over
# the distinct x's; every node of it keeps the sorted y's of the points under it and a bottom-up tree over just those.
# Rectangles are inclusive, x1..x2 by y1..y2, and their corners can be any integers, given or not. Every point starts
# empty and queries only see points that have been set: a min / max over no set point is None; a gcd / xor / OR over
# none is 0.
class PointsSegTree2D:
    __slots__ = ("n", "pts", "vals", "xs", "ys", "off", "cnt", "mn", "gc", "xr", "orr")

    # O(N log N) -- points: every (x, y) a point operation (pointGet, pointAdd, ...) will use, as pairs of integers
    # (negative is fine, repeats are fine); not rectangle or corner coordinates, those can be anything. Needs at least
    # one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsSegTree2D: needs at least one point")
        pts = self.pts = sorted(set(map(tuple, points)))
        self.vals = [None] * len(pts)
        xs = self.xs = sorted({x for x, _ in pts})
        n = self.n = len(xs)
        lists = [[] for _ in range(2 * n)]  # per x-node: the distinct y's under it, ascending
        for x, y in sorted(pts, key=lambda p: p[1]):
            p = bisect_left(xs, x) + n
            while p:
                lst = lists[p]
                if not lst or lst[-1] != y:
                    lst.append(y)
                p >>= 1
        off = self.off = [0] * (2 * n)
        cnt = self.cnt = [0] * (2 * n)
        ys = self.ys = []
        for p in range(1, 2 * n):
            off[p] = len(ys)
            cnt[p] = len(lists[p])
            ys += lists[p]
        self.mn = [POS] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
        self.gc = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
        self.xr = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
        self.orr = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])

    # where (x, y) is in the sorted points
    def _index(self, x, y, name):
        pts = self.pts
        i = bisect_left(pts, (x, y))
        if i == len(pts) or pts[i] != (x, y):
            raise IndexError(f"{name}: ({x}, {y}) is not one of the points given to the constructor")
        return i

    # point (x, y) = v, then every node above it
    def _set(self, x, y, v):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        mn, gc, xr, orr = self.mn, self.gc, self.xr, self.orr
        p = bisect_left(xs, x) + self.n
        vMin = v  # this aggregate over the points with this y under x-node p
        vGcd = v  # this aggregate over the points with this y under x-node p
        vXor = v  # this aggregate over the points with this y under x-node p
        vOr = v  # this aggregate over the points with this y under x-node p
        while True:
            o = off[p]
            c = cnt[p]
            base = 2 * o
            k = bisect_left(ys, y, o, o + c) - o + c
            mn[base + k] = vMin
            gc[base + k] = vGcd
            xr[base + k] = vXor
            orr[base + k] = vOr
            k >>= 1
            while k:
                lhs = mn[base + 2 * k]
                rhs = mn[base + 2 * k + 1]
                mn[base + k] = lhs if lhs < rhs else rhs
                gc[base + k] = gcd(gc[base + 2 * k], gc[base + 2 * k + 1])
                xr[base + k] = xr[base + 2 * k] ^ xr[base + 2 * k + 1]
                orr[base + k] = orr[base + 2 * k] | orr[base + 2 * k + 1]
                k >>= 1
            if p == 1:
                break
            s = p ^ 1  # the other half of the parent: does it have this y too?
            o = off[s]
            c = cnt[s]
            j = bisect_left(ys, y, o, o + c)
            if j < o + c and ys[j] == y:
                j += o + c
                cand = mn[j]
                if cand < vMin:
                    vMin = cand
                vGcd = gcd(vGcd, gc[j])
                vXor ^= xr[j]
                vOr |= orr[j]
            p >>= 1

    # O(log N) -- the value at (x, y), None if it was never set; needs (x, y) to be one of the points given, else
    # IndexError
    def pointGet(self, x, y):
        return self.vals[self._index(x, y, "pointGet")]

    # O(log^2 N) gcds -- the point (x, y) becomes v (it may go down as well as up); needs (x, y) to be one of the points
    # given, else IndexError
    def pointAssign(self, x, y, v):
        self.vals[self._index(x, y, "pointAssign")] = v
        self._set(x, y, v)

    # O(log^2 N) gcds -- adds v to the point (x, y); an empty point becomes v; needs (x, y) to be one of the points
    # given, else IndexError
    def pointAdd(self, x, y, v):
        i = self._index(x, y, "pointAdd")
        cur = self.vals[i]
        if cur is not None:
            v += cur
        self.vals[i] = v
        self._set(x, y, v)

    # O(log^2 N) gcds -- the point (x, y) becomes max(itself, v); an empty point becomes v; needs (x, y) to be one of
    # the points given, else IndexError
    def pointChmax(self, x, y, v):
        i = self._index(x, y, "pointChmax")
        cur = self.vals[i]
        if cur is None or v > cur:
            self.vals[i] = v
            self._set(x, y, v)

    # O(log^2 N) gcds -- the point (x, y) becomes min(itself, v); an empty point becomes v; needs (x, y) to be one of
    # the points given, else IndexError
    def pointChmin(self, x, y, v):
        i = self._index(x, y, "pointChmin")
        cur = self.vals[i]
        if cur is None or v < cur:
            self.vals[i] = v
            self._set(x, y, v)

    def _minOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        mn = self.mn
        res = POS
        l = bisect_left(xs, x1) + self.n
        r = bisect_right(xs, x2) + self.n
        while l < r:
            if l & 1:
                o = off[l]
                c = cnt[l]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        cand = mn[base + lo]
                        if cand < res:
                            res = cand
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        cand = mn[base + hi]
                        if cand < res:
                            res = cand
                    lo >>= 1
                    hi >>= 1
                l += 1
            if r & 1:
                r -= 1
                o = off[r]
                c = cnt[r]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        cand = mn[base + lo]
                        if cand < res:
                            res = cand
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        cand = mn[base + hi]
                        if cand < res:
                            res = cand
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return None if res == POS else res

    # O(log^2 N) -- min of the set points with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); needs x1 <= x2
    # and y1 <= y2, else IndexError
    def rectMin(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectMin: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._minOf(x1, y1, x2, y2)

    # O(1) -- min of every set point (None if there are none)
    def minAll(self):
        res = self.mn[2 * self.off[1] + 1]
        return None if res == POS else res

    # O(log^2 N) -- min of the set points with x <= the given x and y <= the given y (None if there are none); any
    # integers
    def minLteLte(self, x, y):
        return self._minOf(NEG, NEG, x, y)

    # O(log^2 N) -- min of the set points with x <= the given x and y >= the given y (None if there are none); any
    # integers
    def minLteGte(self, x, y):
        return self._minOf(NEG, y, x, POS)

    # O(log^2 N) -- min of the set points with x >= the given x and y <= the given y (None if there are none); any
    # integers
    def minGteLte(self, x, y):
        return self._minOf(x, NEG, POS, y)

    # O(log^2 N) -- min of the set points with x >= the given x and y >= the given y (None if there are none); any
    # integers
    def minGteGte(self, x, y):
        return self._minOf(x, y, POS, POS)

    def _gcdOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        gc = self.gc
        res = 0
        l = bisect_left(xs, x1) + self.n
        r = bisect_right(xs, x2) + self.n
        while l < r:
            if l & 1:
                o = off[l]
                c = cnt[l]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res = gcd(res, gc[base + lo])
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res = gcd(res, gc[base + hi])
                    lo >>= 1
                    hi >>= 1
                l += 1
            if r & 1:
                r -= 1
                o = off[r]
                c = cnt[r]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res = gcd(res, gc[base + lo])
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res = gcd(res, gc[base + hi])
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return res

    # O(log^2 N + log U) -- gcd of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs x1
    # <= x2 and y1 <= y2, else IndexError
    def rectGcd(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectGcd: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._gcdOf(x1, y1, x2, y2)

    # O(1) -- gcd of every set point (0 if there are none)
    def gcdAll(self):
        return abs(self.gc[2 * self.off[1] + 1])

    def _xorOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        xr = self.xr
        res = 0
        l = bisect_left(xs, x1) + self.n
        r = bisect_right(xs, x2) + self.n
        while l < r:
            if l & 1:
                o = off[l]
                c = cnt[l]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res ^= xr[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res ^= xr[base + hi]
                    lo >>= 1
                    hi >>= 1
                l += 1
            if r & 1:
                r -= 1
                o = off[r]
                c = cnt[r]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res ^= xr[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res ^= xr[base + hi]
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return res

    # O(log^2 N) -- xor of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs x1 <= x2 and
    # y1 <= y2, else IndexError
    def rectXor(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectXor: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._xorOf(x1, y1, x2, y2)

    # O(1) -- xor of every set point (0 if there are none)
    def xorAll(self):
        return self.xr[2 * self.off[1] + 1]

    def _orOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        orr = self.orr
        res = 0
        l = bisect_left(xs, x1) + self.n
        r = bisect_right(xs, x2) + self.n
        while l < r:
            if l & 1:
                o = off[l]
                c = cnt[l]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res |= orr[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res |= orr[base + hi]
                    lo >>= 1
                    hi >>= 1
                l += 1
            if r & 1:
                r -= 1
                o = off[r]
                c = cnt[r]
                base = 2 * o
                lo = bisect_left(ys, y1, o, o + c) - o + c
                hi = bisect_right(ys, y2, o, o + c) - o + c
                while lo < hi:
                    if lo & 1:
                        res |= orr[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res |= orr[base + hi]
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return res

    # O(log^2 N) -- OR of the set points with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs x1 <= x2
    # and y1 <= y2, else IndexError
    def rectOr(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectOr: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._orOf(x1, y1, x2, y2)

    # O(1) -- OR of every set point (0 if there are none)
    def orAll(self):
        return self.orr[2 * self.off[1] + 1]
