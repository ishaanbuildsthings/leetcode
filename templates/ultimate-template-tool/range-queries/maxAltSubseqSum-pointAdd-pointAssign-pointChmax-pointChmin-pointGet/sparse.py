# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/maxAltSubseqSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet/sparse.py
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
# Max alternating subsequence sum +a - b + c ... with point updates, over any index range [lo, hi] (huge or negative is
# fine); every position starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros.
# Each node keeps the summary (pp, pm, mp, mm); merging is not commutative, so a query folds a left and a right
# accumulator, tracking each node's length k (a node at level s covers 2^s slots).



from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


class SparseAltSumTree:
    __slots__ = ("lo", "hi", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
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

    # O(logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        t = self.t
        p = self.size + i - self.lo
        t[p ^ SALT] = (val, NEG, NEG, -val)
        p >>= 1
        k = 1  # length of p's children
        while p:
            a, b = t.get((2 * p) ^ SALT), t.get((2 * p + 1) ^ SALT)
            t[p ^ SALT] = self._merge(self._zero(k) if a is None else a, self._zero(k) if b is None else b)
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
                v = self._zero(k) if v is None else v
                left = v if left is None else self._merge(left, v)
                l += 1
            if r & 1:
                r -= 1
                v = t.get(r ^ SALT)
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

    # O(logU) -- best alternating sum +x - y + z ... over the non-empty subsequences of a[l..r]; needs
    # lo <= l <= r <= hi, else IndexError
    def maxAltSubseqSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"maxAltSubseqSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        res = self._query(l, r)
        return max(res[0], res[1])

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
