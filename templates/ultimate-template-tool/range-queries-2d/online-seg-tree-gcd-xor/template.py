# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-gcd-xor/template.py
# @operations: gcdAll pointAdd pointAssign pointChmax pointChmin pointGet rectGcd rectXor xorAll
# @data-structure-type: seg-tree
# @input: online
# @complexities:
#   gcdAll: 1
#   pointAdd: log^2(U)*log(U) ?
#   pointAssign: log^2(U)*log(U) ?
#   pointChmax: log^2(U)*log(U) ?
#   pointChmin: log^2(U)*log(U) ?
#   pointGet: log(U)
#   rectGcd: log^2(U)+log(U) ?
#   rectXor: log^2(U)
#   xorAll: 1
#   build: 1
# @memory:
#   layout: sparse
#   node: gc[1*log^2(U)] xr[1*log^2(U)]
#   tags: none
#   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
#   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point

from math import gcd



# Dynamic 2D segment tree (gcd, xor): point updates and any-rectangle queries over any coordinate range [xLo, xHi] by
# [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the size of a
# coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will be updated
# can be listed before the first call, the points-known templates are much lighter. A segment tree over x whose nodes
# are made only where touched, each owning a segment tree over y made the same way. Rectangles are inclusive: x1..x2
# by y1..y2. Every cell starts at 0.
class DynamicSegTree2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "gc", "xr")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] 0; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"DynamicSegTree2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, xHi = {xHi}, "
                             f"yLo = {yLo}, yHi = {yHi}")
        self.xLo = xLo
        self.xHi = xHi
        self.yLo = yLo
        self.yHi = yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root)
        self.yLeft = [0]  # y-node 0 = nothing there: its aggregates are what an untouched range gives
        self.yRight = [0]
        self.gc = [0]
        self.xr = [0]

    # cell (x, y) = v, then every node above it
    def _set(self, x, y, v):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        gc, xr = self.gc, self.xr
        yLo, yHi = self.yLo, self.yHi
        path = []  # the x-nodes from the root down to the one for x alone
        p = 1
        lo = self.xLo
        hi = self.xHi
        while True:
            path.append(p)
            if lo == hi:
                break
            mid = (lo + hi) >> 1
            if x <= mid:
                if not xLeft[p]:
                    xLeft[p] = len(xLeft)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                p = xLeft[p]
                hi = mid
            else:
                if not xRight[p]:
                    xRight[p] = len(xLeft)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                p = xRight[p]
                lo = mid + 1
        vGcd = v  # this aggregate over row y of the x-node being written
        vXor = v  # this aggregate over row y of the x-node being written
        below = 0  # the x-node just written (a child of the next one up)
        for i in range(len(path) - 1, -1, -1):
            p = path[i]
            if below:
                q = xTree[xRight[p] if xLeft[p] == below else xLeft[p]]  # the other child: what does it hold at y?
                lo = yLo
                hi = yHi
                while q and lo < hi:
                    mid = (lo + hi) >> 1
                    if y <= mid:
                        q = yLeft[q]
                        hi = mid
                    else:
                        q = yRight[q]
                        lo = mid + 1
                vGcd = gcd(vGcd, gc[q])
                vXor ^= xr[q]
            below = p
            q = xTree[p]
            if not q:
                q = xTree[p] = len(yLeft)
                yLeft.append(0)
                yRight.append(0)
                gc.append(0)
                xr.append(0)
            ypath = []
            lo = yLo
            hi = yHi
            while lo < hi:
                ypath.append(q)
                mid = (lo + hi) >> 1
                if y <= mid:
                    if not yLeft[q]:
                        yLeft[q] = len(yLeft)
                        yLeft.append(0)
                        yRight.append(0)
                        gc.append(0)
                        xr.append(0)
                    q = yLeft[q]
                    hi = mid
                else:
                    if not yRight[q]:
                        yRight[q] = len(yLeft)
                        yLeft.append(0)
                        yRight.append(0)
                        gc.append(0)
                        xr.append(0)
                    q = yRight[q]
                    lo = mid + 1
            gc[q] = vGcd
            xr[q] = vXor
            for j in range(len(ypath) - 1, -1, -1):
                q = ypath[j]
                a = yLeft[q]
                b = yRight[q]
                gc[q] = gcd(gc[a], gc[b])
                xr[q] = xr[a] ^ xr[b]

    # the value held at exactly (x, y) in this aggregate's array (what an untouched cell gives if nothing is there)
    def _cell(self, x, y):
        xLeft, xRight, yLeft, yRight = self.xLeft, self.xRight, self.yLeft, self.yRight
        p = 1
        lo = self.xLo
        hi = self.xHi
        while p and lo < hi:
            mid = (lo + hi) >> 1
            if x <= mid:
                p = xLeft[p]
                hi = mid
            else:
                p = xRight[p]
                lo = mid + 1
        q = self.xTree[p]
        lo = self.yLo
        hi = self.yHi
        while q and lo < hi:
            mid = (lo + hi) >> 1
            if y <= mid:
                q = yLeft[q]
                hi = mid
            else:
                q = yRight[q]
                lo = mid + 1
        return self.xr[q]

    # O(log U) -- the value at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._cell(x, y)

    # O(log^2 U) gcds -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo <= y
    # <= yHi, else IndexError
    def pointAssign(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        self._set(x, y, v)

    # O(log^2 U) gcds -- adds v to the cell at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointAdd(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        self._set(x, y, cur + v)

    # O(log^2 U) gcds -- the cell at (x, y) becomes max(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointChmax(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if v > cur:
            self._set(x, y, v)

    # O(log^2 U) gcds -- the cell at (x, y) becomes min(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointChmin(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if v < cur:
            self._set(x, y, v)

    def _gcdOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        gc = self.gc
        yLo, yHi = self.yLo, self.yHi
        res = 0
        stack = [(1, self.xLo, self.xHi)]
        while stack:
            p, lo, hi = stack.pop()
            if p and not (x1 <= lo and hi <= x2):
                mid = (lo + hi) >> 1
                if x1 <= mid:
                    stack.append((xLeft[p], lo, mid))
                if x2 > mid:
                    stack.append((xRight[p], mid + 1, hi))
                continue
            # this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
            inner = [(xTree[p], yLo, yHi)]
            while inner:
                q, lo, hi = inner.pop()
                if q and not (y1 <= lo and hi <= y2):
                    mid = (lo + hi) >> 1
                    if y1 <= mid:
                        inner.append((yLeft[q], lo, mid))
                    if y2 > mid:
                        inner.append((yRight[q], mid + 1, hi))
                    continue
                res = gcd(res, gc[q])
        return res

    # O(log^2 U + log U) -- gcd of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo
    # <= y1 <= y2 <= yHi, else IndexError
    def rectGcd(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectGcd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._gcdOf(x1, y1, x2, y2)

    # O(1) -- gcd of the whole range
    def gcdAll(self):
        return abs(self.gc[self.xTree[1]])

    def _xorOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        xr = self.xr
        yLo, yHi = self.yLo, self.yHi
        res = 0
        stack = [(1, self.xLo, self.xHi)]
        while stack:
            p, lo, hi = stack.pop()
            if p and not (x1 <= lo and hi <= x2):
                mid = (lo + hi) >> 1
                if x1 <= mid:
                    stack.append((xLeft[p], lo, mid))
                if x2 > mid:
                    stack.append((xRight[p], mid + 1, hi))
                continue
            # this x-node is wholly inside x1..x2 (or nothing was ever set under it): its y-tree answers for all its x's
            inner = [(xTree[p], yLo, yHi)]
            while inner:
                q, lo, hi = inner.pop()
                if q and not (y1 <= lo and hi <= y2):
                    mid = (lo + hi) >> 1
                    if y1 <= mid:
                        inner.append((yLeft[q], lo, mid))
                    if y2 > mid:
                        inner.append((yRight[q], mid + 1, hi))
                    continue
                res ^= xr[q]
        return res

    # O(log^2 U) -- xor of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <=
    # y2 <= yHi, else IndexError
    def rectXor(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectXor: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._xorOf(x1, y1, x2, y2)

    # O(1) -- xor of the whole range
    def xorAll(self):
        return self.xr[self.xTree[1]]
