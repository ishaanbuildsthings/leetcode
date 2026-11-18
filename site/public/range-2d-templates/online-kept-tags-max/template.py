# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/online-kept-tags-max/template.py
# @operations: pointChmax pointGet rectChmax
# @data-structure-type: seg-tree-kept-tags
# @input: online
# @empty-cells: yes
# @complexities:
#   pointChmax: log^2(U)
#   pointGet: log^2(U)
#   rectChmax: log^2(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: tag[4*log^2(U)]
#   other: yLeft[4*log^2(U)] yRight[4*log^2(U)] xLeft[2*log(U)] xRight[2*log(U)] xTree[2*log(U)]
#   note: sizes are per update: a rectangle makes up to about 2 log U x-nodes and, in each of the O(log U) it tags, up to about 2 log U y-nodes


NEG = float("-inf")  # no update has reached it


# Rectangle chmax with point reads over a huge coordinate range, nothing known up front: O(log^2 U) per rectChmax,
# O(log^2 U) per pointGet, and up to about 4 log^2 U new nodes per rectChmax. A dynamic tree over x whose every node
# owns a dynamic tree over y, nodes made only where an update goes. rectChmax(x1, y1, x2, y2, v) leaves v as a tag
# on the O(log U) x-nodes that make up x1..x2, and in each of them on the O(log U) y-nodes that make up y1..y2;
# pointGet(x, y) takes the max of the tags on the way down to (x, y). Tags are never pushed down, which works because
# chmax never has to be undone. A cell no update has reached reads None.
class OnlineRectChmax2D:
    __slots__ = ("xLo", "xHi", "yLo", "yHi", "xLeft", "xRight", "xTree", "yLeft", "yRight", "tag")

    # O(1) -- every cell of [xLo, xHi] by [yLo, yHi] unreached; needs xLo <= xHi and yLo <= yHi, else ValueError
    def __init__(self, xLo, xHi, yLo, yHi):
        if xLo > xHi or yLo > yHi:
            raise ValueError(f"OnlineRectChmax2D: needs xLo <= xHi and yLo <= yHi, got xLo = {xLo}, xHi = {xHi}, "
                             f"yLo = {yLo}, yHi = {yHi}")
        self.xLo, self.xHi, self.yLo, self.yHi = xLo, xHi, yLo, yHi
        self.xLeft = [0, 0]  # x-node 0 = nothing there, x-node 1 = the root
        self.xRight = [0, 0]
        self.xTree = [0, 0]  # an x-node's own y-tree (its root, 0 = none yet)
        self.yLeft = [0]  # y-node 0 = nothing there
        self.yRight = [0]
        self.tag = [NEG]

    # the y-tree rooted at root (0: a new one): y1..y2 become max(themselves, v); returns its root
    def _cols(self, root, y1, y2, v):
        yLeft, yRight, tag = self.yLeft, self.yRight, self.tag
        if not root:
            root = len(tag)
            yLeft.append(0)
            yRight.append(0)
            tag.append(NEG)
        stack = [(root, self.yLo, self.yHi)]
        while stack:
            q, lo, hi = stack.pop()
            if y1 <= lo and hi <= y2:
                if v > tag[q]:
                    tag[q] = v
                continue
            mid = (lo + hi) >> 1
            if y1 <= mid:
                if not yLeft[q]:
                    yLeft[q] = len(tag)
                    yLeft.append(0)
                    yRight.append(0)
                    tag.append(NEG)
                stack.append((yLeft[q], lo, mid))
            if y2 > mid:
                if not yRight[q]:
                    yRight[q] = len(tag)
                    yLeft.append(0)
                    yRight.append(0)
                    tag.append(NEG)
                stack.append((yRight[q], mid + 1, hi))
        return root

    # O(log^2 U) -- every cell with x1 <= x <= x2 and y1 <= y <= y2 becomes max(itself, v) (one never reached becomes
    # v); needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, else IndexError
    def rectChmax(self, x1, y1, x2, y2, v):
        if not (self.xLo <= x1 <= x2 <= self.xHi and self.yLo <= y1 <= y2 <= self.yHi):
            raise IndexError(f"rectChmax: needs xLo <= x1 <= x2 <= xHi and yLo <= y1 <= y2 <= yHi, got x1 = {x1}, "
                             f"y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._update(x1, y1, x2, y2, v)

    def _update(self, x1, y1, x2, y2, v):
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        stack = [(1, self.xLo, self.xHi)]
        while stack:
            p, lo, hi = stack.pop()
            if x1 <= lo and hi <= x2:
                xTree[p] = self._cols(xTree[p], y1, y2, v)
                continue
            mid = (lo + hi) >> 1
            if x1 <= mid:
                if not xLeft[p]:
                    xLeft[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                stack.append((xLeft[p], lo, mid))
            if x2 > mid:
                if not xRight[p]:
                    xRight[p] = len(xTree)
                    xLeft.append(0)
                    xRight.append(0)
                    xTree.append(0)
                stack.append((xRight[p], mid + 1, hi))

    # O(log^2 U) -- the cell (x, y) becomes max(itself, v) (one never reached becomes v); needs xLo <= x <= xHi and
    # yLo <= y <= yHi, else IndexError
    def pointChmax(self, x, y, v):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointChmax: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        self._update(x, y, x, y, v)

    # O(log^2 U) -- the value at (x, y), None if no update has reached it; needs xLo <= x <= xHi and yLo <= y <= yHi,
    # else IndexError
    def pointGet(self, x, y):
        if not (self.xLo <= x <= self.xHi and self.yLo <= y <= self.yHi):
            raise IndexError(f"pointGet: needs xLo <= x <= xHi and yLo <= y <= yHi, got x = {x}, y = {y}")
        xLeft, xRight, xTree = self.xLeft, self.xRight, self.xTree
        yLeft, yRight, tag = self.yLeft, self.yRight, self.tag
        res = NEG
        p, lo, hi = 1, self.xLo, self.xHi
        while p:
            q, ylo, yhi = xTree[p], self.yLo, self.yHi
            while q:
                if tag[q] > res:
                    res = tag[q]
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
        return None if res == NEG else res
