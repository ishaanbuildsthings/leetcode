# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/sparse.py
# @operations: leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum rightmostSuffixSumGtX rightmostSuffixSumGteX
# @data-structure-type: BIT
# @complexities:
#   leftmostPrefixSumGtX: log(U)
#   leftmostPrefixSumGteX: log(U)
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointChmax: log(U)
#   pointChmin: log(U)
#   pointGet: log(U)
#   rangeSum: log(U)
#   rightmostSuffixSumGtX: log(U)
#   rightmostSuffixSumGteX: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: tree[1*log(U)]
#   tags: none
#   other: children[2*log(U)]
#   note: per update, the O(logU) entries above each changed position; the prefix / suffix-sum searches need every a[i] >= 0; they return lo - 1 (-1 when lo = 0) when nothing qualifies. A Fenwick tree in a dict (no child pointers)

# Point add, range sum, and the first index where a running sum from l reaches x.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseBIT:
    __slots__ = ("lo", "hi", "n", "d")

    # O(1)
    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}

    # O(logU) -- tree[x] += v at offset x
    def _add(self, x, v):
        d, n = self.d, self.n
        x += 1
        while x <= n:
            d[x] = d.get(x, 0) + v
            x += x & -x

    # O(logU) -- tree[0] + ... + tree[x] (0 for x = -1)
    def _prefix(self, x):
        d = self.d
        s = 0
        x += 1
        while x > 0:
            s += d.get(x, 0)
            x &= x - 1
        return s

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self._add(i - self.lo, delta)

    # O(logU) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        if l > r:
            return 0
        return self._prefix(r - self.lo) - self._prefix(l - 1 - self.lo)

    # O(logU) -- a[i]
    def pointGet(self, i):
        return self.rangeSum(i, i)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self._add(i - self.lo, val - self.pointGet(i))

    # O(logU) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        cur = self.pointGet(i)
        if val > cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        cur = self.pointGet(i)
        if val < cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- smallest offset x with prefix(x) >= target (> target if strict), or n. Binary lifting over the
    # Fenwick tree; needs every a[i] >= 0.
    def _lowerBound(self, target, strict):
        d, n = self.d, self.n
        pos = acc = 0
        step = 1 << (n.bit_length() - 1)
        while step:
            nxt = pos + step
            if nxt <= n:
                v = acc + d.get(nxt, 0)
                if v < target or (strict and v == target):
                    pos, acc = nxt, v
            step >>= 1
        return pos

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGteX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, False))
        return i if i <= r else self.lo - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.
    def leftmostPrefixSumGtX(self, l, r, x):
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, True))
        return i if i <= r else self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1. Needs every a[i] >= 0.
    # That is the last i with a[lo] + ... + a[i - 1] <= prefix(r) - x: one binary lift.
    def rightmostSuffixSumGteX(self, l, r, x):
        t = self._prefix(r - self.lo) - x
        if t < 0:
            return self.lo - 1
        i = min(r, self.lo + self._lowerBound(t, True))
        return i if i >= l else self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1. Needs every a[i] >= 0.
    def rightmostSuffixSumGtX(self, l, r, x):
        t = self._prefix(r - self.lo) - x
        if t <= 0:
            return self.lo - 1
        i = min(r, self.lo + self._lowerBound(t, False))
        return i if i >= l else self.lo - 1
