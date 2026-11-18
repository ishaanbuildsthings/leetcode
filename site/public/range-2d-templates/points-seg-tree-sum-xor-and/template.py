# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-seg-tree-sum-xor-and/template.py
# @operations: andAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectSum rectXor sumAll xorAll
# @data-structure-type: seg-tree
# @input: points
# @complexities:
#   andAll: 1
#   pointAdd: log^2(N)
#   pointAssign: log^2(N)
#   pointChmax: log^2(N)
#   pointChmin: log^2(N)
#   pointGet: log(N)
#   rectAnd: log^2(N)
#   rectSum: log^2(N)
#   rectXor: log^2(N)
#   sumAll: 1
#   xorAll: 1
#   build: N*log(N)
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N*log(N)] xr[2*N*log(N)] an[2*N*log(N)]
#   tags: none
#   other: ys[1*N*log(N)] pts[2*N] vals[1*N] xs[1*N] off[2*N] cnt[2*N]
#   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's column tree is twice its list

from bisect import bisect_left, bisect_right


# 2D segment tree over points known up front (sum, xor, AND): point updates and any-rectangle queries in O(log^2 N),
# with N log N memory whatever the coordinates are (any integers, negative is fine). The constructor takes every (x,
# y) that will ever be updated. A bottom-up tree over the distinct x's; every node of it keeps the sorted y's of the
# points under it and a bottom-up tree over just those. Rectangles are inclusive, x1..x2 by y1..y2, and their corners
# can be any integers, given or not. Every point given starts at 0.
class PointsSegTree2D:
    __slots__ = ("n", "pts", "vals", "xs", "ys", "off", "cnt", "sm", "xr", "an")

    # O(N log N) -- points: every (x, y) that will ever be updated, as pairs of integers (negative is fine, repeats are
    # fine); needs at least one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsSegTree2D: needs at least one point")
        pts = self.pts = sorted(set(map(tuple, points)))
        self.vals = [0] * len(pts)
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
        self.sm = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
        self.xr = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])
        self.an = [0] * (2 * len(ys))  # x-node p's column tree is [2 * off[p], 2 * off[p] + 2 * cnt[p])

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
        sm, xr, an = self.sm, self.xr, self.an
        p = bisect_left(xs, x) + self.n
        vSum = v  # this aggregate over the points with this y under x-node p
        vXor = v  # this aggregate over the points with this y under x-node p
        vAnd = v  # this aggregate over the points with this y under x-node p
        while True:
            o = off[p]
            c = cnt[p]
            base = 2 * o
            k = bisect_left(ys, y, o, o + c) - o + c
            sm[base + k] = vSum
            xr[base + k] = vXor
            an[base + k] = vAnd
            k >>= 1
            while k:
                sm[base + k] = sm[base + 2 * k] + sm[base + 2 * k + 1]
                xr[base + k] = xr[base + 2 * k] ^ xr[base + 2 * k + 1]
                an[base + k] = an[base + 2 * k] & an[base + 2 * k + 1]
                k >>= 1
            if p == 1:
                break
            s = p ^ 1  # the other half of the parent: does it have this y too?
            o = off[s]
            c = cnt[s]
            j = bisect_left(ys, y, o, o + c)
            if j < o + c and ys[j] == y:
                j += o + c
                vSum += sm[j]
                vXor ^= xr[j]
                vAnd &= an[j]
            p >>= 1

    # O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointGet(self, x, y):
        return self.vals[self._index(x, y, "pointGet")]

    # O(log^2 N) -- the point (x, y) becomes v (it may go down as well as up); needs (x, y) to be one of the points
    # given, else IndexError
    def pointAssign(self, x, y, v):
        self.vals[self._index(x, y, "pointAssign")] = v
        self._set(x, y, v)

    # O(log^2 N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointAdd(self, x, y, v):
        i = self._index(x, y, "pointAdd")
        cur = self.vals[i]
        v += cur
        self.vals[i] = v
        self._set(x, y, v)

    # O(log^2 N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmax(self, x, y, v):
        i = self._index(x, y, "pointChmax")
        cur = self.vals[i]
        if v > cur:
            self.vals[i] = v
            self._set(x, y, v)

    # O(log^2 N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmin(self, x, y, v):
        i = self._index(x, y, "pointChmin")
        cur = self.vals[i]
        if v < cur:
            self.vals[i] = v
            self._set(x, y, v)

    def _sumOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        sm = self.sm
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
                        res += sm[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res += sm[base + hi]
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
                        res += sm[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res += sm[base + hi]
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return res

    # O(log^2 N) -- sum of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2
    # and y1 <= y2, else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectSum: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._sumOf(x1, y1, x2, y2)

    # O(1) -- sum of every point
    def sumAll(self):
        return self.sm[2 * self.off[1] + 1]

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

    # O(log^2 N) -- xor of the points with x1 <= x <= x2 and y1 <= y <= y2 (0 if no point is there); needs x1 <= x2
    # and y1 <= y2, else IndexError
    def rectXor(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectXor: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._xorOf(x1, y1, x2, y2)

    # O(1) -- xor of every point
    def xorAll(self):
        return self.xr[2 * self.off[1] + 1]

    def _andOf(self, x1, y1, x2, y2):
        xs, ys, off, cnt = self.xs, self.ys, self.off, self.cnt
        an = self.an
        res = -1
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
                        res &= an[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res &= an[base + hi]
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
                        res &= an[base + lo]
                        lo += 1
                    if hi & 1:
                        hi -= 1
                        res &= an[base + hi]
                    lo >>= 1
                    hi >>= 1
            l >>= 1
            r >>= 1
        return res

    # O(log^2 N) -- AND of the points with x1 <= x <= x2 and y1 <= y <= y2 (-1 (every bit set) if no point is there);
    # needs x1 <= x2 and y1 <= y2, else IndexError
    def rectAnd(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectAnd: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._andOf(x1, y1, x2, y2)

    # O(1) -- AND of every point
    def andAll(self):
        return self.an[2 * self.off[1] + 1]
