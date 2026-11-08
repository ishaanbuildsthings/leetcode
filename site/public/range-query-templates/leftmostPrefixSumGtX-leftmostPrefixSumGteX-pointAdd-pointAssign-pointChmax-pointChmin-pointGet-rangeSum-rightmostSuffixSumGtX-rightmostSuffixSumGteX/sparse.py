# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/sparse.py
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


from random import getrandbits

SALT = getrandbits(62)  # dict keys are salted positions, so no fixed input can make the dict collide


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
            d[x ^ SALT] = d.get(x ^ SALT, 0) + v
            x += x & -x

    # O(logU) -- tree[0] + ... + tree[x] (0 for x = -1)
    def _prefix(self, x):
        d = self.d
        s = 0
        x += 1
        while x > 0:
            s += d.get(x ^ SALT, 0)
            x &= x - 1
        return s

    # O(logU) -- a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self._add(i - self.lo, delta)

    # O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l > r:
            return 0
        return self._prefix(r - self.lo) - self._prefix(l - 1 - self.lo)

    # O(logU) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self.rangeSum(i, i)

    # O(logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        self._add(i - self.lo, val - self.pointGet(i))

    # O(logU) -- a[i] = max(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmax(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmax: needs lo <= i <= hi, got i = {i}")
        cur = self.pointGet(i)
        if val > cur:
            self._add(i - self.lo, val - cur)

    # O(logU) -- a[i] = min(a[i], val); needs lo <= i <= hi, else IndexError
    def pointChmin(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointChmin: needs lo <= i <= hi, got i = {i}")
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
                v = acc + d.get(nxt ^ SALT, 0)
                if v < target or (strict and v == target):
                    pos, acc = nxt, v
            step >>= 1
        return pos

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1. Needs every a[i] >= 0.; needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostPrefixSumGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, False))
        return i if i <= r else self.lo - 1

    # O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1. Needs every a[i] >= 0.; needs
    # lo <= l <= r <= hi, else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"leftmostPrefixSumGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i = max(l, self.lo + self._lowerBound(self._prefix(l - 1 - self.lo) + x, True))
        return i if i <= r else self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1. Needs every a[i] >= 0. That is the last i
    # with a[lo] + ... + a[i - 1] <= prefix(r) - x: one binary lift.; needs lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostSuffixSumGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        t = self._prefix(r - self.lo) - x
        if t < 0:
            return self.lo - 1
        i = min(r, self.lo + self._lowerBound(t, True))
        return i if i >= l else self.lo - 1

    # O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1. Needs every a[i] >= 0.; needs
    # lo <= l <= r <= hi, else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rightmostSuffixSumGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        t = self._prefix(r - self.lo) - x
        if t <= 0:
            return self.lo - 1
        i = min(r, self.lo + self._lowerBound(t, False))
        return i if i >= l else self.lo - 1
