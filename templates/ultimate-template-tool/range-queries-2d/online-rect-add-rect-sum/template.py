# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-rect-add-rect-sum/template.py
# @operations: pointAdd pointGet rectAdd rectSum sumAll sumGteGte sumGteLte sumLteGte sumLteLte
# @data-structure-type: BIT
# @input: online
# @model: area
# @complexities:
#   pointAdd: log^2(U)
#   pointGet: log^2(U)
#   rectAdd: log^2(U)
#   rectSum: log^2(U)
#   sumAll: 1
#   sumGteGte: log^2(U)
#   sumGteLte: log^2(U)
#   sumLteGte: log^2(U)
#   sumLteLte: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: s0[4*log^2(U)] sx[4*log^2(U)] sy[4*log^2(U)] sxy[4*log^2(U)]
#   tags: none
#   other: yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[4*log(U)] xRight[4*log(U)] xTree[4*log(U)]
#   note: sizes are per update: a rect add is up to four marks, each making up to about log U x-nodes and log U y-nodes under each


# Rectangle add and rectangle sum over a huge coordinate range, nothing known up front: O(log^2 U) per operation, and
# up to about 4 log^2 U new nodes per rectAdd. A rect add is four point marks at its corners (+v, -v, -v, +v), and the
# sum of the cells with x <= X and y <= Y comes from four sums over the marks below and left of (X, Y): of d, d * x, d
# * y and d * x * y, which a dynamic tree over x whose every node owns a dynamic tree over y keeps (coordinates are
# counted from xLo and yLo). Every cell starts at 0, and sums are true area sums: a rect add of v on a 3 by 4 rectangle
# adds 12 * v.
class OnlineRectAddRectSum2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "W", "H", "xLeft", "xRight",
                 "xTree", "yLeft", "yRight", "s0", "sx", "sy", "sxy", "total")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectAddRectSum2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, xHi = {xHi}, "
                             f"yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.W = xHi - xLo  # (marks sit at 0..W by 0..H, counted from xLo and yLo)
        self.H = yHi - yLo
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.s0 = [0]  # per y-node: the sums of d, d * x, d * y, d * x * y over the marks below it
        self.sx = [0]
        self.sy = [0]
        self.sxy = [0]
        self.total = 0

    def _newY(self):
        self.yLeft.append(0)
        self.yRight.append(0)
        self.s0.append(0)
        self.sx.append(0)
        self.sy.append(0)
        self.sxy.append(0)
        return len(self.s0) - 1

    # a mark of d at (x, y), counted from (xLo, yLo)
    def _mark(self, x, y, d):
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, s0, sx, sy, sxy = self.yLeft, self.yRight, self.s0, self.sx, self.sy, self.sxy
        dx = d * x
        dy = d * y
        dxy = dx * y
        p, lo, hi = 1, 0, self.W
        while True:
            if not xTree[p]:
                xTree[p] = self._newY()
            q, ylo, yhi = xTree[p], 0, self.H
            while True:
                s0[q] += d
                sx[q] += dx
                sy[q] += dy
                sxy[q] += dxy
                if ylo == yhi:
                    break
                mid = (ylo + yhi) >> 1
                if y <= mid:
                    if not yLeft[q]:
                        yLeft[q] = self._newY()
                    q, yhi = yLeft[q], mid
                else:
                    if not yRight[q]:
                        yRight[q] = self._newY()
                    q, ylo = yRight[q], mid + 1
            if lo == hi:
                break
            mid = (lo + hi) >> 1
            side = xLeft if x <= mid else xRight
            if not side[p]:
                side[p] = len(xTree)
                xLeft.append(0)
                xRight.append(0)
                xTree.append(0)
            if x <= mid:
                p, hi = side[p], mid
            else:
                p, lo = side[p], mid + 1

    # the sum of the cells with x <= X and y <= Y, counted from (xLo, yLo) (X, Y in -1..W, -1..H)
    def _prefix(self, X, Y):
        if X < 0 or Y < 0:
            return 0
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, s0, sx, sy, sxy = self.yLeft, self.yRight, self.s0, self.sx, self.sy, self.sxy
        a = b = c = e = 0
        whole = []  # the x-nodes that make up 0..X
        p, lo, hi = 1, 0, self.W
        while p:
            if hi <= X:
                whole.append(p)
                break
            mid = (lo + hi) >> 1
            if X <= mid:
                p, hi = xLeft[p], mid
            else:
                if xLeft[p]:
                    whole.append(xLeft[p])
                p, lo = xRight[p], mid + 1
        for p in whole:
            q, ylo, yhi = xTree[p], 0, self.H
            while q:
                if yhi <= Y:
                    a += s0[q]
                    b += sx[q]
                    c += sy[q]
                    e += sxy[q]
                    break
                mid = (ylo + yhi) >> 1
                if Y <= mid:
                    q, yhi = yLeft[q], mid
                else:
                    k = yLeft[q]
                    if k:
                        a += s0[k]
                        b += sx[k]
                        c += sy[k]
                        e += sxy[k]
                    q, ylo = yRight[q], mid + 1
        return (X + 1) * (Y + 1) * a - (Y + 1) * b - (X + 1) * c + e

    def _add(self, x1, y1, x2, y2, v):
        self.total += v * (x2 - x1 + 1) * (y2 - y1 + 1)
        a, b = x1 - self.xLo, x2 - self.xLo + 1
        c, e = y1 - self.yLo, y2 - self.yLo + 1
        self._mark(a, c, v)
        if b <= self.W:  # (a mark past the range never reaches a query)
            self._mark(b, c, -v)
        if e <= self.H:
            self._mark(a, e, -v)
        if b <= self.W and e <= self.H:
            self._mark(b, e, v)

    def _sum(self, x1, y1, x2, y2):
        a, b = x1 - self.xLo - 1, x2 - self.xLo
        c, e = y1 - self.yLo - 1, y2 - self.yLo
        return self._prefix(b, e) - self._prefix(a, e) - self._prefix(b, c) + self._prefix(a, c)

    # O(log^2 U) -- adds v to every cell with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <=
    # y1 <= y2 <= yHi, else IndexError
    def rectAdd(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectAdd: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._add(x1, y1, x2, y2, v)

    # O(log^2 U) -- adds v to the cell (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointAdd(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAdd: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._add(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y); needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._sum(x, y, x, y)

    # O(log^2 U) -- sum of the cells with x1 <= x <= x2 and y1 <= y <= y2; needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <=
    # y2 <= yHi, else IndexError
    def rectSum(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectSum: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._sum(x1, y1, x2, y2)

    # O(1) -- sum of every cell
    def sumAll(self):
        return self.total

    # O(log^2 U) -- sum of the cells with x <= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def sumLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        x -= self.xLo
        y -= self.yLo
        return self._prefix(x, y)

    # O(log^2 U) -- sum of the cells with x <= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def sumLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        x -= self.xLo
        y -= self.yLo
        return self._prefix(x, self.H) - self._prefix(x, y - 1)

    # O(log^2 U) -- sum of the cells with x >= the given x and y <= the given y; needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def sumGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        x -= self.xLo
        y -= self.yLo
        return self._prefix(self.W, y) - self._prefix(x - 1, y)

    # O(log^2 U) -- sum of the cells with x >= the given x and y >= the given y; needs xLo <= x <= xHi and yLo <= y <=
    # yHi, else IndexError
    def sumGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"sumGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        x -= self.xLo
        y -= self.yLo
        return self.total - self._prefix(x - 1, self.H) - self._prefix(self.W, y - 1) + self._prefix(x - 1, y - 1)
