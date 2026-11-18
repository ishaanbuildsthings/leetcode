# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries-2d/points-kept-tags-min/template.py
# @operations: pointChmin pointGet rectChmin
# @data-structure-type: seg-tree-kept-tags
# @input: points
# @empty-cells: yes
# @complexities:
#   pointChmin: log(N)
#   pointGet: log^2(N)
#   rectChmin: log^2(N)
#   build: N*log(N)
# @memory:
#   layout: 2n-iterative
#   node: none
#   tags: tag[2*N*log(N)]
#   other: ys[1*N*log(N)] xs[1*N] off[2*N] cnt[2*N] given[2*N]
#   note: every point's y is listed in each of the O(log N) x-nodes above it; an x-node's y-tree is twice its list


from bisect import bisect_left, bisect_right

POS = float("inf")  # no update has reached it


# Rectangle chmin with point reads over points known up front (any integers, negative is fine): O(log^2 N) per
# rectChmax, O(log^2 N) per pointGet, N log N memory. A tree over the distinct x's, where every x-node keeps a tree over
# the y's of its own points. rectChmin(x1, y1, x2, y2, v) leaves v as a tag on the O(log N) x-nodes that make up x1..x2,
# and in each of them on the O(log N) y-nodes that make up y1..y2; pointGet(x, y) takes the min of the tags on the way
# from (x, y) up. Tags are never pushed down, which works because chmin never has to be undone. The points given are the
# ones you will read or chmin one at a time; a rectangle's corners can be anything. A point no update has reached reads
# None.
class PointsRectChmin2D:
    __slots__ = ("X", "xs", "ys", "off", "cnt", "tag", "given")

    # O(N log N) -- points: every (x, y) you will call pointGet or pointChmin on, as pairs of integers (negative is
    # fine, repeats are fine); needs at least one, else ValueError
    def __init__(self, points):
        if not points:
            raise ValueError("PointsRectChmin2D: needs at least one point")
        given = self.given = set(map(tuple, points))
        xs = self.xs = sorted({x for x, _ in given})
        X = self.X = len(xs)
        lists = [[] for _ in range(2 * X)]
        for x, y in given:
            lists[X + bisect_left(xs, x)].append(y)
        for i in range(X, 2 * X):
            lists[i].sort()
        for i in range(X - 1, 0, -1):  # an x-node's y's: its two halves' y's, merged, each y once
            a, b = lists[2 * i], lists[2 * i + 1]
            merged = []
            p = q = 0
            while p < len(a) or q < len(b):
                if q == len(b) or (p < len(a) and a[p] <= b[q]):
                    y = a[p]
                    p += 1
                else:
                    y = b[q]
                    q += 1
                if not merged or merged[-1] != y:
                    merged.append(y)
            lists[i] = merged
        off = self.off = [0] * (2 * X)
        cnt = self.cnt = [0] * (2 * X)
        ys = self.ys = []
        for i in range(1, 2 * X):
            off[i] = len(ys)
            cnt[i] = len(lists[i])
            ys += lists[i]
        # x-node i's y-tree: tag[2 * off[i] + k], its leaves at k = cnt[i] + (the y's place in the x-node's list)
        self.tag = [POS] * (2 * len(ys))

    # x-node i: the y's in y1..y2 become min(themselves, v)
    def _cols(self, i, y1, y2, v):
        ys, o, m, tag = self.ys, self.off[i], self.cnt[i], self.tag
        a = bisect_left(ys, y1, o, o + m) - o + m
        b = bisect_right(ys, y2, o, o + m) - o + m
        base = 2 * o
        while a < b:
            if a & 1:
                if v < tag[base + a]:
                    tag[base + a] = v
                a += 1
            if b & 1:
                b -= 1
                if v < tag[base + b]:
                    tag[base + b] = v
            a >>= 1
            b >>= 1

    # O(log^2 N) -- every given point with x1 <= x <= x2 and y1 <= y <= y2 becomes min(itself, v) (one never
    # reached becomes v); any integers; needs x1 <= x2 and y1 <= y2, else IndexError
    def rectChmin(self, x1, y1, x2, y2, v):
        if x1 > x2 or y1 > y2:
            raise IndexError(f"rectChmin: needs x1 <= x2 and y1 <= y2, got x1 = {x1}, y1 = {y1}, x2 = {x2}, y2 = {y2}")
        xs, X = self.xs, self.X
        l = bisect_left(xs, x1) + X
        r = bisect_right(xs, x2) + X
        while l < r:
            if l & 1:
                self._cols(l, y1, y2, v)
                l += 1
            if r & 1:
                r -= 1
                self._cols(r, y1, y2, v)
            l >>= 1
            r >>= 1

    # O(log N) -- the point (x, y) becomes min(itself, v) (one never reached becomes v); needs (x, y) to be one of
    # the points given, else IndexError
    def pointChmin(self, x, y, v):
        if (x, y) not in self.given:
            raise IndexError(f"pointChmin: ({x}, {y}) is not one of the points given to the constructor")
        i = bisect_left(self.xs, x) + self.X
        o, m = self.off[i], self.cnt[i]
        k = 2 * o + bisect_left(self.ys, y, o, o + m) - o + m
        if v < self.tag[k]:
            self.tag[k] = v

    # O(log^2 N) -- the value at (x, y), None if no update has reached it; needs (x, y) to be one of the points given,
    # else IndexError
    def pointGet(self, x, y):
        if (x, y) not in self.given:
            raise IndexError(f"pointGet: ({x}, {y}) is not one of the points given to the constructor")
        ys, off, cnt, tag = self.ys, self.off, self.cnt, self.tag
        res = POS
        i = bisect_left(self.xs, x) + self.X
        while i:
            o, m = off[i], cnt[i]
            base = 2 * o
            k = bisect_left(ys, y, o, o + m) - o + m
            while k:
                cand = tag[base + k]
                if cand < res:
                    res = cand
                k >>= 1
            i >>= 1
        return None if res == POS else res
