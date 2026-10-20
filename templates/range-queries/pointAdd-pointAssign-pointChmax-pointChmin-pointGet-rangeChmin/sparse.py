# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmin/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeChmin
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeChmin: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: none
#   tags: tag[4*log(U)]
#   other: children[8*log(U)]
#   note: per update, the nodes a range update visits (at most 4 per level; a point write creates its path and the path's siblings); a node's one field is its pending tag, or at a leaf its value. A dict keyed by heap index

INF = float("inf")

# Range chmin + point ops, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Internal nodes hold a pending tag, leaves hold values. The tags commute, so a range update just tags its
# O(logU) covering nodes and pointGet folds the tags on the leaf's root path. A point write first pushes the tags
# on its path down, so they stop applying to it. Sparse: a dict keyed by heap index over a power-of-two cover of
# [lo, hi]; a missing internal node has no tag, a missing leaf is 0.


class SparseRangeChminTree:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.t = {}

    # node x takes tag v (a leaf into its value)
    def _apply(self, x, v):
        t = self.t
        if x >= self.size:
            a = t.get(x, 0)
            t[x] = a if a < v else v
        else:
            a = t.get(x, INF)
            t[x] = a if a < v else v

    # O(logU) -- a[i] = min(a[i], v) for i in [l, r]
    def rangeChmin(self, l, r, v):
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                self._apply(l, v)
                l += 1
            if r & 1:
                r -= 1
                self._apply(r, v)
            l >>= 1
            r >>= 1

    # O(logU) -- move the tags on leaf p's root path down, so none of them is pending above p
    def _push(self, p):
        t = self.t
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            v = t.pop(x, None)
            if v is not None and v != INF:
                self._apply(2 * x, v)
                self._apply(2 * x + 1, v)

    # O(logU) -- a[i]
    def pointGet(self, i):
        t = self.t
        p = self.size + i - self.lo
        x = t.get(p, 0)
        a = INF  # the tags on the path, composed
        p >>= 1
        while p:
            v = t.get(p)
            if v is not None:
                a = a if a < v else v
            p >>= 1
        a, v = x, a
        return a if a < v else v

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        self.t[p] = val

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        t[p] = (t.get(p, 0) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        if val > t.get(p, 0):
            t[p] = val

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        p = self.size + i - self.lo
        self._push(p)
        t = self.t
        if val < t.get(p, 0):
            t[p] = val
