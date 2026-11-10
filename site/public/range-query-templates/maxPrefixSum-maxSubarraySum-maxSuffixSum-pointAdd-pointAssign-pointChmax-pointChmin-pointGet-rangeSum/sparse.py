# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/maxPrefixSum-maxSubarraySum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/sparse.py
# @operations: maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
# @data-structure-type: seg-tree
# @complexities:
#   maxPrefixSum: log(U)
#   maxSubarraySum: log(U)
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
#   node: sm[1*log(U)] pre[1*log(U)] suf[1*log(U)] best[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path; pieces are non-empty, so a block of zeros summarizes to all zeros; a dict keyed by heap index, a missing key is a block of zeros

# Max subarray / prefix / suffix sum + range sum with point updates, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
# Each node keeps the summary (sm, pre, suf, best); merging is not commutative, so a query folds a left and a right
# accumulator, tracking each node's length k (a node at level s covers 2^s slots).
ZERO = (0, 0, 0, 0)  # the summary of any block of zeros


from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


class SparseMaxSubarrayTree:
    __slots__ = ("lo", "hi", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {}

    @staticmethod
    def _merge(a, b):
        return (a[0] + b[0], max(a[1], a[0] + b[1]), max(b[2], b[0] + a[2]), max(a[3], b[3], a[2] + b[1]))

    # O(logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        t = self.t
        p = self.size + i - self.lo
        t[p ^ SALT] = (val, val, val, val)
        p >>= 1
        k = 1  # length of p's children
        while p:
            a, b = t.get((2 * p) ^ SALT), t.get((2 * p + 1) ^ SALT)
            t[p ^ SALT] = self._merge(ZERO if a is None else a, ZERO if b is None else b)
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
                v = t.get(l ^ SALT)
                v = ZERO if v is None else v
                left = v if left is None else self._merge(left, v)
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r ^ SALT)
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

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        res = self._query(l, r)
        return res[0]

    # O(logU) -- best sum of a non-empty prefix of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def maxPrefixSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"maxPrefixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        res = self._query(l, r)
        return res[1]

    # O(logU) -- best sum of a non-empty suffix of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def maxSuffixSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"maxSuffixSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        res = self._query(l, r)
        return res[2]

    # O(logU) -- best sum of a non-empty subarray of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def maxSubarraySum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"maxSubarraySum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        res = self._query(l, r)
        return res[3]

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return (lambda v: 0 if v is None else v[0])(self.t.get((self.size + i - self.lo) ^ SALT))

    # O(logU) -- a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU) -- a[i] = max(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU) -- a[i] = min(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
