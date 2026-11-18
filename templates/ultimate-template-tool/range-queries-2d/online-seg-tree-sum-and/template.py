# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-seg-tree-sum-and/template.py
# @operations: andAll pointAdd pointAssign pointChmax pointChmin pointGet rectAnd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
# @data-structure-type: seg-tree
# @input: online
# @complexities:
#   andAll: 1
#   pointAdd: log^2(U)
#   pointAssign: log^2(U)
#   pointChmax: log^2(U)
#   pointChmin: log^2(U)
#   pointGet: log(U)
#   rectAnd: log^2(U)
#   rectSum: log^2(U)
#   sumAll: 1
#   sumGteGte: log^2(U)
#   sumGteLte: log^2(U)
#   sumLteGte: log^2(U)
#   sumLteLte: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[1*log^2(U)] an[1*log^2(U)]
#   tags: none
#   other: yLeft[1*log^2(U)] yRight[1*log^2(U)] xLeft[1*log(U)] xRight[1*log(U)] xTree[1*log(U)]
#   note: sizes are per update: it makes up to log U x-nodes, and a y-path of up to log U nodes in each x-node above the point



# Dynamic 2D segment tree (sum, AND): point updates and any-rectangle queries over any coordinate range [xLo, xHi] by
# [yLo, yHi] (as big as +-10^18, negative is fine), with nothing known up front. O(log^2 U) per op, U = the size of a
# coordinate range, and up to log^2 U new nodes per update: the heaviest option. When every point that will be updated
# can be listed before the first call, the points-known templates are much lighter. A segment tree over x whose nodes
# are made only where touched, each owning a segment tree over y made the same way. Rectangles are inclusive: x1..x2
# by y1..y2. Every cell starts at 0 (so an AND over a rectangle with a cell nobody set is 0).
class DynamicSegTree2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "sm", "an")

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
        self.sm = [0]
        self.an = [0]

    # cell (x, y) = v, then every node above it
    def _set(self, x, y, v):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        sm, an = self.sm, self.an
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
        vSum = v  # this aggregate over row y of the x-node being written
        vAnd = v  # this aggregate over row y of the x-node being written
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
                vSum += sm[q]
                vAnd &= an[q]
            below = p
            q = xTree[p]
            if not q:
                q = xTree[p] = len(yLeft)
                yLeft.append(0)
                yRight.append(0)
                sm.append(0)
                an.append(0)
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
                        sm.append(0)
                        an.append(0)
                    q = yLeft[q]
                    hi = mid
                else:
                    if not yRight[q]:
                        yRight[q] = len(yLeft)
                        yLeft.append(0)
                        yRight.append(0)
                        sm.append(0)
                        an.append(0)
                    q = yRight[q]
                    lo = mid + 1
            sm[q] = vSum
            an[q] = vAnd
            for j in range(len(ypath) - 1, -1, -1):
                q = ypath[j]
                a = yLeft[q]
                b = yRight[q]
                sm[q] = sm[a] + sm[b]
                an[q] = an[a] & an[b]

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
        return self.sm[q]

    # O(log U) -- the value at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._cell(x, y)

    # O(log^2 U) -- the cell at (x, y) becomes v (it may go down as well as up); needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def pointAssign(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        self._set(x, y, v)

    # O(log^2 U) -- adds v to the cell at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointAdd(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        self._set(x, y, cur + v)

    # O(log^2 U) -- the cell at (x, y) becomes max(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointChmax(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if v > cur:
            self._set(x, y, v)

    # O(log^2 U) -- the cell at (x, y) becomes min(itself, v); needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointChmin(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        cur = self._cell(x, y)
        if v < cur:
            self._set(x, y, v)

    def _sumOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        sm = self.sm
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
                res += sm[q]
        return res

    # O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <=
    # y2 <= yHi, else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectSum: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._sumOf(x1, y1, x2, y2)

    # O(1) -- sum of the whole range
    def sumAll(self):
        return self.sm[self.xTree[1]]

    # O(log^2 U) -- sum of the set cells with x <= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def sumLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._sumOf(self.xLo, self.yLo, x, y)

    # O(log^2 U) -- sum of the set cells with x <= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def sumLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._sumOf(self.xLo, y, x, self.yHi)

    # O(log^2 U) -- sum of the set cells with x >= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def sumGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._sumOf(x, self.yLo, self.xHi, y)

    # O(log^2 U) -- sum of the set cells with x >= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <=
    # y <= yHi, else IndexError
    def sumGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}, "
                             f"xLo = {self.xLo}, xHi = {self.xHi}, yLo = {self.yLo}, yHi = {self.yHi}")
        return self._sumOf(x, y, self.xHi, self.yHi)

    def _andOf(self, x1, y1, x2, y2):
        xLeft, xRight, xTree, yLeft, yRight = self.xLeft, self.xRight, self.xTree, self.yLeft, self.yRight
        an = self.an
        yLo, yHi = self.yLo, self.yHi
        res = -1
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
                res &= an[q]
        return res

    # O(log^2 U) -- AND of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <=
    # y2 <= yHi, else IndexError
    def rectAnd(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectAnd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}, xLo = {self.xLo}, xHi = {self.xHi}, "
                             f"yLo = {self.yLo}, yHi = {self.yHi}")
        return self._andOf(x1, y1, x2, y2)

    # O(1) -- AND of the whole range
    def andAll(self):
        return self.an[self.xTree[1]]
