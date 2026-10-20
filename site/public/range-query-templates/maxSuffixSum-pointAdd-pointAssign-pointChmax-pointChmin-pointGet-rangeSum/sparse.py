# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/sparse.py
# @operations: maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   maxSuffixSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeSum: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: sm[1*log(U)] suf[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path; pieces are non-empty, so a block of zeros summarizes to all zeros; a dict keyed by heap index, a missing key is a block of zeros

# Max suffix sum + range sum with point updates, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
# Each node keeps the summary (sm, suf); merging is not commutative, so a query folds a left and a right
# accumulator, tracking each node's length k (a node at level s covers 2^s slots).
ZERO = (0, 0)  # the summary of any block of zeros


class SparseMaxSuffixSumTree:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {}

    @staticmethod
    def _merge(a, b):
        return (a[0] + b[0], max(b[1], b[0] + a[1]))

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        t = self.t
        p = self.size + i - self.lo
        t[p] = (val, val)
        p >>= 1
        k = 1  # length of p's children
        while p:
            a, b = t.get(2 * p), t.get(2 * p + 1)
            t[p] = self._merge(ZERO if a is None else a, ZERO if b is None else b)
            p >>= 1
            k <<= 1

    # O(logU) -- summary of a[l..r]
    def _query(self, l, r):
        t = self.t
        left = right = None
        l += self.size - self.lo
        r += self.size - self.lo + 1
        k = 1
        while l < r:
            if l & 1:
                v = t.get(l)
                v = ZERO if v is None else v
                left = v if left is None else self._merge(left, v)
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r)
                v = ZERO if v is None else v
                right = v if right is None else self._merge(v, right)
            l >>= 1
            r >>= 1
            k <<= 1
        if left is None:
            return right
        if right is None:
            return left
        return self._merge(left, right)

    # O(logU)
    def rangeSum(self, l, r):
        res = self._query(l, r)
        return res[0]

    # O(logU)
    def maxSuffixSum(self, l, r):
        res = self._query(l, r)
        return res[1]

    # O(logU) -- a[i]
    def pointGet(self, i):
        return (lambda v: 0 if v is None else v[0])(self.t.get(self.size + i - self.lo))

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
