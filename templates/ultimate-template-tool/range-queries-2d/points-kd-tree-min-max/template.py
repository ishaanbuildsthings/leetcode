# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-kd-tree-min-max/template.py
# @operations: maxAll maxGteGte maxGteLte maxLteGte maxLteLte minAll minGteGte minGteLte minLteGte minLteLte pointAdd pointAssign pointChmax pointChmin pointGet rectAdd rectAssign rectChmax rectChmin rectMax rectMin
# @data-structure-type: kd-tree
# @input: points
# @complexities:
#   maxAll: 1
#   maxGteGte: sqrt(N)
#   maxGteLte: sqrt(N)
#   maxLteGte: sqrt(N)
#   maxLteLte: sqrt(N)
#   minAll: 1
#   minGteGte: sqrt(N)
#   minGteLte: sqrt(N)
#   minLteGte: sqrt(N)
#   minLteLte: sqrt(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rectAdd: sqrt(N)
#   rectAssign: sqrt(N)
#   rectChmax: sqrt(N)
#   rectChmin: sqrt(N)
#   rectMax: sqrt(N)
#   rectMin: sqrt(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: mn[2*N] mx[2*N]
#   tags: addTag[2*N] loTag[2*N] hiTag[2*N]
#   other: xMin[2*N] xMax[2*N] yMin[2*N] yMax[2*N] pts[2*N] pos[1*N]
#   note: a binary tree over the points in k-d order (2N - 1 nodes), each node with its points' bounding box

from bisect import bisect_left

NEG = float("-inf")  # the max of no points; also "no lower bound" on a coordinate
POS = float("inf")  # the min of no points; also "no upper bound" on a coordinate


# K-d tree with lazy tags (min, max): rectangle add, assign, chmax and chmin together with rectangle min, max, over
# points known up front (any integers, negative is fine). O(sqrt N) per rectangle op, O(log N) per point op, linear
# memory. A tree of trees can't do rectangle updates with these queries (a tag can't be pushed down its outer tree);
# this can, because it is one tree: the points are split in half by x, each half by y, and so on, every node keeps the
# bounding box of its points, and a rectangle op only opens the nodes whose box the rectangle's border crosses (about
# sqrt N of them). The constructor takes every (x, y) that will ever be used; every point starts at 0. Rectangles are
# inclusive, x1..x2 by y1..y2, and their corners can be any integers; a rectangle update touches the given points
# inside it. A min / max over a rectangle with no given point in it is None.
class KdTree2D:
    __slots__ = ("n", "pts", "pos", "xMin", "xMax", "yMin", "yMax", "addTag", "loTag", "hiTag", "mn", "mx")

    # O(N log N) -- points: every (x, y) that will ever be used, as pairs of integers (negative is fine, repeats are
    # fine); needs at least one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("KdTree2D: needs at least one point")
        pts = self.pts = sorted(set(map(tuple, points)))
        n = self.n = len(pts)
        size = 2 * n
        xMin = self.xMin = [0] * size
        xMax = self.xMax = [0] * size
        yMin = self.yMin = [0] * size
        yMax = self.yMax = [0] * size
        pos = self.pos = [0] * n  # pos[i]: where point i (in sorted order) sits in k-d order
        self.addTag = [0] * size
        self.loTag = [NEG] * size  # a node's waiting tag: add addTag, then clamp to loTag..hiTag
        self.hiTag = [POS] * size
        self.mn = [0] * size
        self.mx = [0] * size
        side = [False] * n
        # a node is a stretch l..r of the k-d order; node (l, r) is numbered (l + r) | (l != r), its halves l..mid,
        # mid+1..r.
        # Each node gets its points sorted by (x, y) and by (y, x); splitting keeps both orders, so the build is N log N
        todo = [(0, n - 1, list(range(n)), sorted(range(n), key=lambda i: (pts[i][1], pts[i][0])), 0)]
        while todo:
            l, r, byX, byY, axis = todo.pop()
            node = (l + r) | (l != r)
            xMin[node] = pts[byX[0]][0]
            xMax[node] = pts[byX[-1]][0]
            yMin[node] = pts[byY[0]][1]
            yMax[node] = pts[byY[-1]][1]
            if l == r:
                pos[byX[0]] = l
                continue
            mid = (l + r) >> 1
            half = mid - l + 1
            first = byX[:half] if axis == 0 else byY[:half]
            for i in first:
                side[i] = True
            if axis == 0:
                todo.append((mid + 1, r, byX[half:], [i for i in byY if not side[i]], 1))
                todo.append((l, mid, first, [i for i in byY if side[i]], 1))
            else:
                todo.append((mid + 1, r, [i for i in byX if not side[i]], byY[half:], 0))
                todo.append((l, mid, [i for i in byX if side[i]], first, 0))
            for i in first:
                side[i] = False

    # hands node (l, r)'s waiting tag to its two halves
    def _push(self, node, l, r):
        addTag, loTag, hiTag = self.addTag, self.loTag, self.hiTag
        av = addTag[node]
        lv = loTag[node]
        hv = hiTag[node]
        if not av and lv == NEG and hv == POS:
            return
        mn, mx = self.mn, self.mx
        mid = (l + r) >> 1
        for child in ((l + mid) | (l != mid), (mid + 1 + r) | (mid + 1 != r)):
            addTag[child] += av
            cand = loTag[child] + av
            loTag[child] = lv if cand < lv else hv if cand > hv else cand
            cand = hiTag[child] + av
            hiTag[child] = lv if cand < lv else hv if cand > hv else cand
            cand = mn[child] + av
            mn[child] = lv if cand < lv else hv if cand > hv else cand
            cand = mx[child] + av
            mx[child] = lv if cand < lv else hv if cand > hv else cand
        addTag[node] = 0
        loTag[node] = NEG
        hiTag[node] = POS

    # every given point inside the rectangle: add a, then clamp to lo..hi
    def _update(self, x1, y1, x2, y2, a, lo, hi):
        xMin, xMax, yMin, yMax = self.xMin, self.xMax, self.yMin, self.yMax
        addTag, loTag, hiTag = self.addTag, self.loTag, self.hiTag
        mn, mx = self.mn, self.mx
        push = self._push

        def go(l, r):
            node = (l + r) | (l != r)
            if xMin[node] > x2 or xMax[node] < x1 or yMin[node] > y2 or yMax[node] < y1:
                return
            if x1 <= xMin[node] and xMax[node] <= x2 and y1 <= yMin[node] and yMax[node] <= y2:
                addTag[node] += a
                cand = loTag[node] + a
                loTag[node] = lo if cand < lo else hi if cand > hi else cand
                cand = hiTag[node] + a
                hiTag[node] = lo if cand < lo else hi if cand > hi else cand
                cand = mn[node] + a
                mn[node] = lo if cand < lo else hi if cand > hi else cand
                cand = mx[node] + a
                mx[node] = lo if cand < lo else hi if cand > hi else cand
                return
            push(node, l, r)
            mid = (l + r) >> 1
            go(l, mid)
            go(mid + 1, r)
            left = (l + mid) | (l != mid)
            right = (mid + 1 + r) | (mid + 1 != r)
            lhs = mn[left]
            rhs = mn[right]
            mn[node] = lhs if lhs < rhs else rhs
            lhs = mx[left]
            rhs = mx[right]
            mx[node] = lhs if lhs > rhs else rhs

        go(0, self.n - 1)

    # the aggregates over the given points inside the rectangle, and how many points that is
    def _query(self, x1, y1, x2, y2):
        xMin, xMax, yMin, yMax = self.xMin, self.xMax, self.yMin, self.yMax
        mn, mx = self.mn, self.mx
        push = self._push
        resMin = POS
        resMax = NEG
        count = 0
        stack = [(0, self.n - 1)]
        while stack:
            l, r = stack.pop()
            node = (l + r) | (l != r)
            if xMin[node] > x2 or xMax[node] < x1 or yMin[node] > y2 or yMax[node] < y1:
                continue
            if x1 <= xMin[node] and xMax[node] <= x2 and y1 <= yMin[node] and yMax[node] <= y2:
                count += r - l + 1
                cand = mn[node]
                if cand < resMin:
                    resMin = cand
                cand = mx[node]
                if cand > resMax:
                    resMax = cand
                continue
            push(node, l, r)
            mid = (l + r) >> 1
            stack.append((l, mid))
            stack.append((mid + 1, r))
        return resMin, resMax, count

    # where point (x, y) sits in k-d order, with every tag above it handed down first
    def _open(self, x, y, name):
        pts = self.pts
        i = bisect_left(pts, (x, y))
        if i == len(pts) or pts[i] != (x, y):
            raise IndexError(f"{name}: ({x}, {y}) is not one of the points given to the constructor")
        p = self.pos[i]
        push = self._push
        l = 0
        r = self.n - 1
        while l < r:
            push((l + r) | 1, l, r)
            mid = (l + r) >> 1
            if p <= mid:
                r = mid
            else:
                l = mid + 1
        return p

    # the point at k-d position p becomes v, then every node above it
    def _setLeaf(self, p, v):
        mn, mx = self.mn, self.mx
        mn[2 * p] = v
        mx[2 * p] = v
        path = []
        l = 0
        r = self.n - 1
        while l < r:
            path.append((l, r))
            mid = (l + r) >> 1
            if p <= mid:
                r = mid
            else:
                l = mid + 1
        for l, r in reversed(path):
            mid = (l + r) >> 1
            node = (l + r) | 1
            left = (l + mid) | (l != mid)
            right = (mid + 1 + r) | (mid + 1 != r)
            lhs = mn[left]
            rhs = mn[right]
            mn[node] = lhs if lhs < rhs else rhs
            lhs = mx[left]
            rhs = mx[right]
            mx[node] = lhs if lhs > rhs else rhs

    # O(log N) -- the value at (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointGet(self, x, y):
        return self.mn[2 * self._open(x, y, "pointGet")]

    # O(log N) -- the point (x, y) becomes v; needs (x, y) to be one of the points given, else IndexError
    def pointAssign(self, x, y, v):
        p = self._open(x, y, "pointAssign")
        self._setLeaf(p, v)

    # O(log N) -- adds v to the point (x, y); needs (x, y) to be one of the points given, else IndexError
    def pointAdd(self, x, y, v):
        p = self._open(x, y, "pointAdd")
        self._setLeaf(p, self.mn[2 * p] + v)

    # O(log N) -- the point (x, y) becomes max(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmax(self, x, y, v):
        p = self._open(x, y, "pointChmax")
        if v > self.mn[2 * p]:
            self._setLeaf(p, v)

    # O(log N) -- the point (x, y) becomes min(itself, v); needs (x, y) to be one of the points given, else IndexError
    def pointChmin(self, x, y, v):
        p = self._open(x, y, "pointChmin")
        if v < self.mn[2 * p]:
            self._setLeaf(p, v)

    # O(sqrt N) -- adds v to every given point with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2 and y1 <= y2, else
    # IndexError
    def rectAdd(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectAdd: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        self._update(x1, y1, x2, y2, v, NEG, POS)

    # O(sqrt N) -- every given point becomes v, for the points with x1 <= x <= x2 and y1 <= y <= y2; needs x1 <= x2
    # and y1 <= y2, else IndexError
    def rectAssign(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectAssign: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, "
                             f"y2 = {y2}")
        self._update(x1, y1, x2, y2, 0, v, v)

    # O(sqrt N) -- every given point becomes max(itself, v), for the points with x1 <= x <= x2 and y1 <= y <= y2;
    # needs x1 <= x2 and y1 <= y2, else IndexError
    def rectChmax(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectChmax: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, "
                             f"y2 = {y2}")
        self._update(x1, y1, x2, y2, 0, v, POS)

    # O(sqrt N) -- every given point becomes min(itself, v), for the points with x1 <= x <= x2 and y1 <= y <= y2;
    # needs x1 <= x2 and y1 <= y2, else IndexError
    def rectChmin(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectChmin: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, "
                             f"y2 = {y2}")
        self._update(x1, y1, x2, y2, 0, NEG, v)

    # O(sqrt N) -- min of the given points with x1 <= x <= x2 and y1 <= y <= y2 (None if no point is there); needs x1 <=
    # x2 and y1 <= y2, else IndexError
    def rectMin(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectMin: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        res = self._query(x1, y1, x2, y2)
        return res[0] if res[-1] else None

    # O(1) -- min of every point
    def minAll(self):
        return self.mn[(self.n - 1) | (self.n > 1)]

    # O(sqrt N) -- min of the given points with x <= the given x and y <= the given y (None if there are none); any
    # integers
    def minLteLte(self, x, y):
        res = self._query(NEG, NEG, x, y)
        return res[0] if res[-1] else None

    # O(sqrt N) -- min of the given points with x <= the given x and y >= the given y (None if there are none); any
    # integers
    def minLteGte(self, x, y):
        res = self._query(NEG, y, x, POS)
        return res[0] if res[-1] else None

    # O(sqrt N) -- min of the given points with x >= the given x and y <= the given y (None if there are none); any
    # integers
    def minGteLte(self, x, y):
        res = self._query(x, NEG, POS, y)
        return res[0] if res[-1] else None

    # O(sqrt N) -- min of the given points with x >= the given x and y >= the given y (None if there are none); any
    # integers
    def minGteGte(self, x, y):
        res = self._query(x, y, POS, POS)
        return res[0] if res[-1] else None

    # O(sqrt N) -- max of the given points with x1 <= x <= x2 and y1 <= y <= y2 (None if no point is there); needs x1 <=
    # x2 and y1 <= y2, else IndexError
    def rectMax(self, x1, y1, x2, y2):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectMax: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        res = self._query(x1, y1, x2, y2)
        return res[1] if res[-1] else None

    # O(1) -- max of every point
    def maxAll(self):
        return self.mx[(self.n - 1) | (self.n > 1)]

    # O(sqrt N) -- max of the given points with x <= the given x and y <= the given y (None if there are none); any
    # integers
    def maxLteLte(self, x, y):
        res = self._query(NEG, NEG, x, y)
        return res[1] if res[-1] else None

    # O(sqrt N) -- max of the given points with x <= the given x and y >= the given y (None if there are none); any
    # integers
    def maxLteGte(self, x, y):
        res = self._query(NEG, y, x, POS)
        return res[1] if res[-1] else None

    # O(sqrt N) -- max of the given points with x >= the given x and y <= the given y (None if there are none); any
    # integers
    def maxGteLte(self, x, y):
        res = self._query(x, NEG, POS, y)
        return res[1] if res[-1] else None

    # O(sqrt N) -- max of the given points with x >= the given x and y >= the given y (None if there are none); any
    # integers
    def maxGteGte(self, x, y):
        res = self._query(x, y, POS, POS)
        return res[1] if res[-1] else None
