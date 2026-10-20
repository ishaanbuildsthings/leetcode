# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/maxAltSubseqSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.py
# @operations: maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   maxAltSubseqSum: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: pp[1*log(U)] pm[1*log(U)] mp[1*log(U)] mm[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path; pairs (first sign, last sign) of a block of zeros: a single zero can't start + and end -; a dict keyed by heap index, a missing key is a block of zeros

NEG = float("-inf")
# Max alternating subsequence sum +a - b + c ... with point updates, over any index range [lo, hi] (huge or negative is fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
# Each node keeps the summary (pp, pm, mp, mm); merging is not commutative, so a query folds a left and a right
# accumulator, tracking each node's length k (a node at level s covers 2^s slots).



class SparseAltSumTree:
    __slots__ = ("lo", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo = lo
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {}

    @staticmethod
    def _merge(a, b):
        app, apm, amp, amm = a
        bpp, bpm, bmp, bmm = b
        return (max(app, bpp, app + bmp, apm + bpp),
                max(apm, bpm, app + bmm, apm + bpm),
                max(amp, bmp, amp + bmp, amm + bpp),
                max(amm, bmm, amp + bmm, amm + bpm))
    @staticmethod
    def _zero(k):  # a block of k zeros
        return (0, 0 if k > 1 else NEG, 0 if k > 1 else NEG, 0)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        t = self.t
        p = self.size + i - self.lo
        t[p] = (val, NEG, NEG, -val)
        p >>= 1
        k = 1  # length of p's children
        while p:
            a, b = t.get(2 * p), t.get(2 * p + 1)
            t[p] = self._merge(self._zero(k) if a is None else a, self._zero(k) if b is None else b)
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
                v = self._zero(k) if v is None else v
                left = v if left is None else self._merge(left, v)
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r)
                v = self._zero(k) if v is None else v
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
    def maxAltSubseqSum(self, l, r):
        res = self._query(l, r)
        return max(res[0], res[1])

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
