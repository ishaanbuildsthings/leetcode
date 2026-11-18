# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-kept-tags-rect-max/template.py
# @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte pointChmax pointGet rectChmax rectMax
# @data-structure-type: seg-tree-kept-tags
# @input: online
# @empty-cells: yes
# @complexities:
#   maxAll: 1
#   maxGteGte: log^2(U)
#   maxGteLte: log^2(U)
#   maxLteGte: log^2(U)
#   maxLteLte: log^2(U)
#   pointChmax: log^2(U)
#   pointGet: log^2(U)
#   rectChmax: log^2(U)
#   rectMax: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: yCover[8*log^2(U)] yTouch[8*log^2(U)]
#   other: yLeft[8*log^2(U)] yRight[8*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xCover[2*log(U)] xTouch[2*log(U)]
#   note: sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in the two y-trees of each x-node it meets, up to about 2 log U y-nodes


NEG = float("-inf")  # no update has reached it


# Rectangle chmax and rectangle max over a huge coordinate range, nothing known up front: O(log^2 U) per operation,
# and up to about 8 log^2 U new nodes per update. A dynamic tree over x whose every node owns two dynamic trees over
# y: one for the updates that cover all of its x's, one for the updates that touch any of them. Every y-node keeps the
# same two values for its y's. An update goes into the touch side of every node it meets and the cover side of the
# nodes that make up its rectangle; a query reads the touch side of the nodes that make up its rectangle and the cover
# side of the nodes above them (an update covering a whole node above covers the query's part of it too). Tags are
# never pushed down, which works because chmax never has to be undone and seeing one update twice doesn't change a
# max. A cell no update has reached is empty and queries only see set cells.
class OnlineRectChmaxRectMax2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xCover",
                 "xTouch", "yLeft", "yRight", "yCover", "yTouch", "best")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectChmaxRectMax2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, "
                             f"xHi = {xHi}, yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xCover = [0, 0]  # an x-node's y-tree for the updates covering all of its x's (its root, 0 = none yet)
        self.xTouch = [0, 0]  # ... and its y-tree for the updates touching any of its x's
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.yCover = [NEG]  # the best update covering all of a y-node's y's
        self.yTouch = [NEG]  # the best update touching any of them
        self.best = NEG

    def _newY(self):
        self.yLeft.append(0)
        self.yRight.append(0)
        self.yCover.append(NEG)
        self.yTouch.append(NEG)
        return len(self.yCover) - 1

    # the y-tree rooted at root (0: a new one): y1..y2 become max(themselves, v); returns its root
    def _cols(self, root, y1, y2, v):
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        if not root:
            root = self._newY()
        todo = [(root, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if v > yTouch[q]:
                yTouch[q] = v
            if y1 <= lo and hi <= y2:
                if v > yCover[q]:
                    yCover[q] = v
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = self._newY()
                todo.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = self._newY()
                todo.append((yRight[q], mid + 1, hi))
        return root

    # the max the y-tree rooted at q (0: none) holds for y1..y2
    def _colsBest(self, q, y1, y2):
        if not q:
            return NEG
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        res = NEG
        todo = [(q, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if y1 <= lo and hi <= y2:
                if yTouch[q] > res:
                    res = yTouch[q]
                continue
            if yCover[q] > res:
                res = yCover[q]
            mid = (lo + hi) >> 1
            if y1 <= mid and yLeft[q]:
                todo.append((yLeft[q], lo, mid))
            if y2 > mid and yRight[q]:
                todo.append((yRight[q], mid + 1, hi))
        return res

    def _update(self, x1, y1, x2, y2, v):
        if v > self.best:
            self.best = v
        xLeft, xRight, xCover, xTouch = self.xLeft, self.xRight, self.xCover, self.xTouch
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            xTouch[p] = self._cols(xTouch[p], y1, y2, v)
            if x1 <= lo and hi <= x2:
                xCover[p] = self._cols(xCover[p], y1, y2, v)
                continue
            mid = (lo + hi) >> 1
            for side, a, b in ((xLeft, lo, mid), (xRight, mid + 1, hi)):
                if x1 <= b and a <= x2:
                    if not side[p]:
                        side[p] = len(xCover)
                        xLeft.append(0)
                        xRight.append(0)
                        xCover.append(0)
                        xTouch.append(0)
                    todo.append((side[p], a, b))

    def _query(self, x1, y1, x2, y2):
        xLeft, xRight, xCover, xTouch = self.xLeft, self.xRight, self.xCover, self.xTouch
        res = NEG
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            if x1 <= lo and hi <= x2:
                got = self._colsBest(xTouch[p], y1, y2)
                if got > res:
                    res = got
                continue
            got = self._colsBest(xCover[p], y1, y2)
            if got > res:
                res = got
            mid = (lo + hi) >> 1
            if x1 <= mid and xLeft[p]:
                todo.append((xLeft[p], lo, mid))
            if x2 > mid and xRight[p]:
                todo.append((xRight[p], mid + 1, hi))
        return None if res == NEG else res

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes max(itself, v) (an empty one becomes v);
    # needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectChmax(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectChmax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._update(x1, y1, x2, y2, v)

    # O(log^2 U) -- the cell (x, y) becomes max(itself, v) (an empty one becomes v); needs xLo <= x <= xHi and yLo <= y
    # <= yHi, else IndexError
    def pointChmax(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._update(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), None if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, y, x, y)

    # O(log^2 U) -- max of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); needs xLo <= x1
    # <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectMax(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectMax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._query(x1, y1, x2, y2)

    # O(1) -- max of every set cell (None if there are none)
    def maxAll(self):
        return None if self.best == NEG else self.best

    # O(log^2 U) -- max of the set cells with x <= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(self.xLo, self.yLo, x, y)

    # O(log^2 U) -- max of the set cells with x <= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(self.xLo, y, x, self.yHi)

    # O(log^2 U) -- max of the set cells with x >= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, self.yLo, self.xHi, y)

    # O(log^2 U) -- max of the set cells with x >= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def maxGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"maxGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, y, self.xHi, self.yHi)
