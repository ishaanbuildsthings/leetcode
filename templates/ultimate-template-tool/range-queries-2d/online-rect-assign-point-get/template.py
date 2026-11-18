# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-rect-assign-point-get/template.py
# @operations: pointAssign pointGet rectAssign
# @data-structure-type: seg-tree-kept-tags
# @input: online
# @complexities:
#   pointAssign: log^2(U)
#   pointGet: log^2(U)
#   rectAssign: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: stamp[4*log^2(U)]
#   other: yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)] vals[1]
#   note: sizes are per write: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it marks, up to about 2 log U y-nodes; vals keeps each write's value


# Rectangle assign with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per rectAssign
# and per pointGet, and up to about 4 log^2 U new nodes per rectAssign. A dynamic tree over x whose every node owns a
# dynamic tree over y, nodes made only where a write goes. Every write gets the next timestamp and leaves it at the
# O(log U) x-nodes that make up x1..x2, and in each of them at the O(log U) y-nodes that make up y1..y2. A read takes
# the newest timestamp on its way down to (x, y) and returns the value written then: a newer write always wins, so
# nothing is ever pushed down or undone. A cell no write has reached reads 0.
class OnlineRectAssignPointGet2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "stamp", "vals")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] starts at 0; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectAssignPointGet2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, "
                             f"xHi = {xHi}, yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.stamp = [0]  # the newest timestamp left at a y-node (0 = none)
        self.vals = [0]  # vals[t]: the value written at timestamp t (vals[0] = 0: never written)

    # the y-tree rooted at root (0: a new one): y1..y2 get timestamp t; returns its root
    def _cols(self, root, y1, y2, t):
        yLeft, yRight, stamp = self.yLeft, self.yRight, self.stamp
        if not root:
            root = len(stamp)
            yLeft.append(0)
            yRight.append(0)
            stamp.append(0)
        todo = [(root, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if y1 <= lo and hi <= y2:
                stamp[q] = t
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = len(stamp)
                    yLeft.append(0)
                    yRight.append(0)
                    stamp.append(0)
                todo.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = len(stamp)
                    yLeft.append(0)
                    yRight.append(0)
                    stamp.append(0)
                todo.append((yRight[q], mid + 1, hi))
        return root

    # every cell of the rectangle gets the next timestamp, which stands for v
    def _write(self, x1, y1, x2, y2, v):
        self.vals.append(v)
        t = len(self.vals) - 1
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            if x1 <= lo and hi <= x2:
                xTree[p] = self._cols(xTree[p], y1, y2, t)
                continue
            mid = (lo + hi) >> 1
            if x1 <= mid:
                if not xLeft[p]:
                    xLeft[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                todo.append((xLeft[p], lo, mid))
            if x2 > mid:
                if not xRight[p]:
                    xRight[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                todo.append((xRight[p], mid + 1, hi))

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes v; needs xLo <= x1 <= x2 <= xHi and yLo <=
    # y1 <= y2 <= yHi, else IndexError
    def rectAssign(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectAssign: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._write(x1, y1, x2, y2, v)

    # O(log^2 U) -- the cell (x, y) becomes v; needs xLo <= x <= xHi and yLo <= y <= yHi, else IndexError
    def pointAssign(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointAssign: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._write(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), 0 if no write has reached it; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, stamp = self.yLeft, self.yRight, self.stamp
        best = 0
        p, lo, hi = 1, self.xLo, self.xHi
        while p:
            q, ylo, yhi = xTree[p], self.yLo, self.yHi
            while q:
                if stamp[q] > best:
                    best = stamp[q]
                if ylo == yhi:
                    break
                mid = (ylo + yhi) >> 1
                if y <= mid:
                    q, yhi = yLeft[q], mid
                else:
                    q, ylo = yRight[q], mid + 1
            if lo == hi:
                break
            mid = (lo + hi) >> 1
            if x <= mid:
                p, hi = xLeft[p], mid
            else:
                p, lo = xRight[p], mid + 1
        return self.vals[best]
