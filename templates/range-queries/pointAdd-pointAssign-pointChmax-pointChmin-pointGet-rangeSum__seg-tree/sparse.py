# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum__seg-tree/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path;  a dict keyed by heap index, a missing key is a block of zeros

# Point updates + range sum, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros,
# so only the log U nodes on each updated path exist. Same bottom-up loops as the dense tree.


class SparseSumTree:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {}

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        t = self.t
        p = self.size + i - self.lo
        t[p] = val
        p >>= 1
        while p:
            a, b = t.get(2 * p, 0), t.get(2 * p + 1, 0)
            t[p] = a + b
            p >>= 1

    # O(logU) -- fold of a[l..r]
    def rangeSum(self, l, r):
        t, res = self.t, 0
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                a, b = res, t.get(l, 0)
                res = a + b
                l += 1
            if r & 1:
                r -= 1
                a, b = res, t.get(r, 0)
                res = a + b
            l >>= 1
            r >>= 1
        return res

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.t.get(self.size + i - self.lo, 0)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.pointGet(i):
            self.pointAssign(i, val)
