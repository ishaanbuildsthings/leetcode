# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-min-max-xor-or/template.py
# @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte orAll pointAdd pointAssign pointChmax pointChmin pointGet rectMax rectMin rectOr rectXor xorAll
# @data-structure-type: seg-tree
# @input: online
# @empty-cells: yes
# @complexities:
#   maxAll: 1
#   maxGteGte: log^2(U)
#   maxGteLte: log^2(U)
#   maxLteGte: log^2(U)
#   maxLteLte: log^2(U)
#   minAll: 1
#   minGteGte: log^2(U)
#   minGteLte: log^2(U)
#   minLteGte: log^2(U)
#   minLteLte: log^2(U)
#   orAll: 1
#   pointAdd: log^2(U)
#   pointAssign: log^2(U)
#   pointChmax: log^2(U)
#   pointChmin: log^2(U)
#   pointGet: log(U)
#   rectMax: log^2(U)
#   rectMin: log^2(U)
#   rectOr: log^2(U)
#   rectXor: log^2(U)
#   xorAll: 1
#   build: 1
# @memory:
#   layout: sparse
#   node: mn[1*log^2(U)] mx[1*log^2(U)] xr[1*log^2(U)] orr[1*log^2(U)]
#   tags: none
#   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
#   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point

NEG = float("-inf")  # an empty cell in the max array
POS = float("inf")  # an empty cell in the min array


# Dynamic 2D segment tree (min, max, xor, OR): point updates and any-rectangle queries over any coordinate range [xLo,
# xHi] by [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the
# size of a coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will
# be updated can be listed before the first call, the points-known templates are much lighter. A segment tree over x
# whose nodes are made only where touched, each owning a segment tree over y made the same way. Rectangles are
# inclusive: x1..x2 by y1..y2. Every cell starts empty and queries only see cells that have been set: a min / max over
# no set cell is None; a xor / OR over none is 0.
class DynamicSegTree2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "mn", "mx", "xr", "orr")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else ValueError
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
        self.mn = [POS]
        self.mx = [NEG]
        self.xr = [0]
        self.orr = [0]

    # cell (x, y) = v, then every node above it
    def _set(self, x, y, v):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        mn, mx, xr, orr = self.mn, self.mx, self.xr, self.orr
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
        vMin = v  # this aggregate over row y of the x-node being written
        vMax = v  # this aggregate over row y of the x-node being written
        vXor = v  # this aggregate over row y of the x-node being written
        vOr = v  # this aggregate over row y of the x-node being written
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
                cand = mn[q]
                if cand < vMin:
                    vMin = cand
                cand = mx[q]
                if cand > vMax:
                    vMax = cand
                vXor ^= xr[q]
                vOr |= orr[q]
            below = p
            q = xTree[p]
            if not q:
                q = xTree[p] = len(yLeft)
                yLeft.append(0)
                yRight.append(0)
                mn.append(POS)
                mx.append(NEG)
                xr.append(0)
                orr.append(0)
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
                        mn.append(POS)
                        mx.append(NEG)
                        xr.append(0)
                        orr.append(0)
                    q = yLeft[q]
                    hi = mid
                else:
                    if not yRight[q]:
                        yRight[q] = len(yLeft)
                        yLeft.append(0)
                        yRight.append(0)
                        mn.append(POS)
                        mx.append(NEG)
                        xr.append(0)
                        orr.append(0)
                    q = yRight[q]
                    lo = mid + 1
            mn[q] = vMin
            mx[q] = vMax
            xr[q] = vXor
            orr[q] = vOr
            for j in range(len(ypath) - 1, -1, -1):
                q = ypath[j]
                a = yLeft[q]
                b = yRight[q]
                lhs = mn[a]
                rhs = mn[b]
                mn[q] = lhs if lhs < rhs else rhs
                lhs = mx[a]
                rhs = mx[b]
                mx[q] = lhs if lhs > rhs else rhs
                xr[q] = xr[a] ^ xr[b]
                orr[q] = orr[a] | orr[b]

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
        return self.mx[q]

    # O(log U) -- the value at (x, y), None if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        return None if cur == NEG else cur

    # O(log^2 U) -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def pointAssign(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        self._set(x, y, v)

    # O(log^2 U) -- adds v to the cell at (x, y); an empty cell becomes v; needs xLo <= x <= xHi and yLo <= y <= yHi,
    # else IndexError
    def pointAdd(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        self._set(x, y, v if cur == NEG else cur + v)

    # O(log^2 U) -- the cell at (x, y) becomes max(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def pointChmax(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if cur == NEG or v > cur:
            self._set(x, y, v)

    # O(log^2 U) -- the cell at (x, y) becomes min(itself, v); an empty cell becomes v; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def pointChmin(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if cur == NEG or v < cur:
            self._set(x, y, v)

    def _minOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        mn = self.mn
        yLo, yHi = self.yLo, self.yHi
        res = POS
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
                cand = mn[q]
                if cand < res:
                    res = cand
        return None if res == POS else res

    # O(log^2 U) -- min of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); needs xLo <= x1
    # <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectMin(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectMin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._minOf(x1, y1, x2, y2)

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        res = self.mn[self.xTree[1]]
        return None if res == POS else res

    # O(log^2 U) -- min of the set cells with x <= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._minOf(self.xLo, self.yLo, x, y)

    # O(log^2 U) -- min of the set cells with x <= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._minOf(self.xLo, y, x, self.yHi)

    # O(log^2 U) -- min of the set cells with x >= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._minOf(x, self.yLo, self.xHi, y)

    # O(log^2 U) -- min of the set cells with x >= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._minOf(x, y, self.xHi, self.yHi)

    def _maxOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        mx = self.mx
        yLo, yHi = self.yLo, self.yHi
        res = NEG
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
                cand = mx[q]
                if cand > res:
                    res = cand
        return None if res == NEG else res

    # O(log^2 U) -- max of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); needs xLo <= x1
    # <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectMax(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectMax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._maxOf(x1, y1, x2, y2)

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        res = self.mx[self.xTree[1]]
        return None if res == NEG else res

    # O(log^2 U) -- max of the set cells with x <= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._maxOf(self.xLo, self.yLo, x, y)

    # O(log^2 U) -- max of the set cells with x <= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._maxOf(self.xLo, y, x, self.yHi)

    # O(log^2 U) -- max of the set cells with x >= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._maxOf(x, self.yLo, self.xHi, y)

    # O(log^2 U) -- max of the set cells with x >= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._maxOf(x, y, self.xHi, self.yHi)

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

    # O(log^2 U) -- xor of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs xLo <= x1 <=
    # x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectXor(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectXor: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._xorOf(x1, y1, x2, y2)

    # O(1) -- xor of every set cell (0 if there are none)
    def xorAll(self):
        return self.xr[self.xTree[1]]

    def _orOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        orr = self.orr
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
                res |= orr[q]
        return res

    # O(log^2 U) -- OR of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (0 if there are none); needs xLo <= x1 <=
    # x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectOr(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectOr: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._orOf(x1, y1, x2, y2)

    # O(1) -- OR of every set cell (0 if there are none)
    def orAll(self):
        return self.orr[self.xTree[1]]
