# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeGcd/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)*log(U) ?
#   pointAssign: log(U)*log(U) ?
#   pointChmax: log(U)*log(U) ?
#   pointChmin: log(U)*log(U) ?
#   pointGet: log(U)
#   rangeGcd: 2*log(U) ?
#   build: 1
# @memory:
#   layout: sparse
#   node: v[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, one node per level of the touched path; leaves hold the signed values, internal nodes the gcd of |values|; a dict keyed by heap index, a missing key is a block of zeros

from math import gcd
# Point updates + range gcd (of |values|), over any index range [lo, hi] (huge or negative is fine); every position
# starts at 0.
# Sparse: a dict keyed by heap index over a power-of-two cover of [lo, hi]; a missing key is a block of zeros, so only
# the log U nodes on each updated path exist. Same bottom-up loops as the dense tree.


from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


class SparseGcdTree:
    __slots__ = ("lo", "hi", "size", "t")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; leaf of i is size + (i - lo)
        self.t = {}

    # O(logU * logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        t = self.t
        p = self.size + i - self.lo
        t[p ^ SALT] = val
        p >>= 1
        while p:
            a, b = t.get((2 * p) ^ SALT, 0), t.get((2 * p + 1) ^ SALT, 0)
            t[p ^ SALT] = gcd(a, b)
            p >>= 1

    # O(2 * logU) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0); needs lo <= l <= r <= hi, else IndexError
    def rangeGcd(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeGcd: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        t, res = self.t, 0
        l += self.size - self.lo
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                a, b = res, t.get(l ^ SALT, 0)
                res = gcd(a, b)
                l += 1
            if r & 1:
                r -= 1
                a, b = res, t.get(r ^ SALT, 0)
                res = gcd(a, b)
            l >>= 1
            r >>= 1
        return res

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self.t.get((self.size + i - self.lo) ^ SALT, 0)

    # O(logU * logU) -- a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logU * logU) -- a[i] = max(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logU * logU) -- a[i] = min(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)
