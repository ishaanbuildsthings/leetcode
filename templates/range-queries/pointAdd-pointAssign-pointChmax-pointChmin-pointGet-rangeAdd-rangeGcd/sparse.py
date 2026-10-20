# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeGcd/sparse.py
# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: log(U)*log(U) ?
#   pointAssign: log(U)*log(U) ?
#   pointChmax: log(U)*log(U) ?
#   pointChmin: log(U)*log(U) ?
#   pointGet: log(U)
#   rangeAdd: log(U)*log(U) ?
#   rangeGcd: log(U) ?
#   build: 1
# @memory:
#   layout: sparse
#   node: sum[2*log(U)] g[2*log(U)]
#   tags: none
#   other: children[4*log(U)]
#   note: per range add, the two root paths of the differences it changes; one tree over the differences keeps their sum (prefix sums are point values) and gcd; the gcd costs' second log is of the largest value. Dicts keyed by heap index

# Range add + range gcd + point ops over any index range [lo, hi] (huge or negative is fine); every position
# starts at 0. gcd(a[l], ..., a[r]) == gcd(a[l], a[l+1] - a[l], ..., a[r] - a[r-1]), and a range add only changes
# two adjacent differences. One sparse tree over the differences d[i] = a[i] - a[i-1] (d[lo] = a[lo]) keeps
# their sum (a prefix sum is a point value) and the gcd of their absolute values. Sparse: dicts keyed by heap
# index over a power-of-two cover of [lo, hi]; a missing key is a block of zero differences.

from math import gcd


class SparseRangeAddRangeGcd:
    __slots__ = ("lo", "hi", "size", "s", "g")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.size = 1 << (hi - lo).bit_length()  # a power of two > hi - lo; the leaf of i is size + (i - lo)
        self.s = {}  # sum of the differences under a node
        self.g = {}  # gcd of their absolute values

    # O(logU logV) -- d[i] += x
    def _shiftDiff(self, i, x):
        s, g = self.s, self.g
        p = self.size + i - self.lo
        v = s.get(p, 0) + x
        s[p] = v
        g[p] = abs(v)
        p >>= 1
        while p:
            s[p] = s.get(2 * p, 0) + s.get(2 * p + 1, 0)
            g[p] = gcd(g.get(2 * p, 0), g.get(2 * p + 1, 0))
            p >>= 1

    # O(logU) -- d[lo] + ... + d[i], which is a[i]
    def _prefix(self, i):
        s = self.s
        p = self.size + i - self.lo
        total = s.get(p, 0)
        while p > 1:
            if p & 1:
                total += s.get(p - 1, 0)
            p >>= 1
        return total

    # O(logU) -- adds x to every a[l..r], x may be negative
    def rangeAdd(self, l, r, x):
        if l > r:
            return
        self._shiftDiff(l, x)
        if r < self.hi:
            self._shiftDiff(r + 1, -x)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self._prefix(i)

    # O(logU + logV) -- gcd of a[l..r], always >= 0 (0 only if every value in the range is 0)
    def rangeGcd(self, l, r):
        res = abs(self._prefix(l))
        g = self.g
        l += self.size - self.lo + 1  # the differences strictly inside the range
        r += self.size - self.lo + 1
        while l < r:
            if l & 1:
                res = gcd(res, g.get(l, 0))
                l += 1
            if r & 1:
                r -= 1
                res = gcd(res, g.get(r, 0))
            l >>= 1
            r >>= 1
        return res

    # O(logU logV) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAdd(i, i, delta)

    # O(logU logV) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAdd(i, i, val - self._prefix(i))

    # O(logU logV) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self._prefix(i)
        if val > cur:
            self.rangeAdd(i, i, val - cur)

    # O(logU logV) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self._prefix(i)
        if val < cur:
            self.rangeAdd(i, i, val - cur)
