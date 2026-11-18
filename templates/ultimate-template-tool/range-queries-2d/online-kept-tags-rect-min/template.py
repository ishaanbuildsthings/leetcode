# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-kept-tags-rect-min/template.py
# @operations: minAll minGteGte minGteLte minLteGte minLteLte pointChmin pointGet rectChmin rectMin
# @data-structure-type: seg-tree-kept-tags
# @input: online
# @empty-cells: yes
# @complexities:
#   minAll: 1
#   minGteGte: log^2(U)
#   minGteLte: log^2(U)
#   minLteGte: log^2(U)
#   minLteLte: log^2(U)
#   pointChmin: log^2(U)
#   pointGet: log^2(U)
#   rectChmin: log^2(U)
#   rectMin: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: yCover[8*log^2(U)] yTouch[8*log^2(U)]
#   other: yLeft[8*log^2(U)] yRight[8*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xCover[2*log(U)] xTouch[2*log(U)]
#   note: sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in the two y-trees of each x-node it meets, up to about 2 log U y-nodes


POS = float("inf")  # no update has reached it


# Rectangle chmin and rectangle min over a huge coordinate range, nothing known up front: O(log^2 U) per operation,
# and up to about 8 log^2 U new nodes per update. A dynamic tree over x whose every node owns two dynamic trees over
# y: one for the updates that cover all of its x's, one for the updates that touch any of them. Every y-node keeps the
# same two values for its y's. An update goes into the touch side of every node it meets and the cover side of the
# nodes that make up its rectangle; a query reads the touch side of the nodes that make up its rectangle and the cover
# side of the nodes above them (an update covering a whole node above covers the query's part of it too). Tags are
# never pushed down, which works because chmin never has to be undone and seeing one update twice doesn't change a
# min. A cell no update has reached is empty and queries only see set cells.
class OnlineRectChminRectMin2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xCover",
                 "xTouch", "yLeft", "yRight", "yCover", "yTouch", "best")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] empty; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectChminRectMin2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, "
                             f"xHi = {xHi}, yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xCover = [0, 0]  # an x-node's y-tree for the updates covering all of its x's (its root, 0 = none yet)
        self.xTouch = [0, 0]  # ... and its y-tree for the updates touching any of its x's
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.yCover = [POS]  # the best update covering all of a y-node's y's
        self.yTouch = [POS]  # the best update touching any of them
        self.best = POS

    def _newY(self):
        self.yLeft.append(0)
        self.yRight.append(0)
        self.yCover.append(POS)
        self.yTouch.append(POS)
        return len(self.yCover) - 1

    # the y-tree rooted at root (0: a new one): y1..y2 become min(themselves, v); returns its root
    def _cols(self, root, y1, y2, v):
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        if not root:
            root = self._newY()
        todo = [(root, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if v < yTouch[q]:
                yTouch[q] = v
            if y1 <= lo and hi <= y2:
                if v < yCover[q]:
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

    # the min the y-tree rooted at q (0: none) holds for y1..y2
    def _colsBest(self, q, y1, y2):
        if not q:
            return POS
        yLeft, yRight, yCover, yTouch = self.yLeft, self.yRight, self.yCover, self.yTouch
        res = POS
        todo = [(q, self.yLo, self.yHi)]
        while todo:
            q, lo, hi = todo.pop()
            if y1 <= lo and hi <= y2:
                if yTouch[q] < res:
                    res = yTouch[q]
                continue
            if yCover[q] < res:
                res = yCover[q]
            mid = (lo + hi) >> 1
            if y1 <= mid and yLeft[q]:
                todo.append((yLeft[q], lo, mid))
            if y2 > mid and yRight[q]:
                todo.append((yRight[q], mid + 1, hi))
        return res

    def _update(self, x1, y1, x2, y2, v):
        if v < self.best:
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
        res = POS
        todo = [(1, self.xLo, self.xHi)]
        while todo:
            p, lo, hi = todo.pop()
            if x1 <= lo and hi <= x2:
                got = self._colsBest(xTouch[p], y1, y2)
                if got < res:
                    res = got
                continue
            got = self._colsBest(xCover[p], y1, y2)
            if got < res:
                res = got
            mid = (lo + hi) >> 1
            if x1 <= mid and xLeft[p]:
                todo.append((xLeft[p], lo, mid))
            if x2 > mid and xRight[p]:
                todo.append((xRight[p], mid + 1, hi))
        return None if res == POS else res

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes min(itself, v) (an empty one becomes v);
    # needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectChmin(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectChmin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._update(x1, y1, x2, y2, v)

    # O(log^2 U) -- the cell (x, y) becomes min(itself, v) (an empty one becomes v); needs xLo <= x <= xHi and yLo <= y
    # <= yHi, else IndexError
    def pointChmin(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmin: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._update(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), None if the cell is empty; needs xLo <= x <= xHi and yLo <= y <= yHi, else
    # IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, y, x, y)

    # O(log^2 U) -- min of the set cells with x1 <= x <= x2 and y1 <= y <= y2 (None if there are none); needs xLo <= x1
    # <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectMin(self, x1, y1, x2, y2):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectMin: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        return self._query(x1, y1, x2, y2)

    # O(1) -- min of every set cell (None if there are none)
    def minAll(self):
        return None if self.best == POS else self.best

    # O(log^2 U) -- min of the set cells with x <= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minLteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minLteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(self.xLo, self.yLo, x, y)

    # O(log^2 U) -- min of the set cells with x <= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minLteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minLteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(self.xLo, y, x, self.yHi)

    # O(log^2 U) -- min of the set cells with x >= the given x and y <= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minGteLte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minGteLte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, self.yLo, self.xHi, y)

    # O(log^2 U) -- min of the set cells with x >= the given x and y >= the given y (None if there are none); needs xLo
    # <= x <= xHi and yLo <= y <= yHi, else IndexError
    def minGteGte(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"minGteGte: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        return self._query(x, y, self.xHi, self.yHi)
