# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod/sparse.py
# @operations: pointAdd pointAssign pointGet rangeAddMod
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointGet: log(U)
#   rangeAddMod: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: d[2*log(U)]
#   tags: none
#   other: children[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; a range add changes two differences. A Fenwick tree in a dict (no child pointers)

# Range add, point get, all % MOD: prefix sums of the difference array d[i] = a[i] - a[i - 1].
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseRangeAddBITMod:
    __slots__ = ("lo", "hi", "n", "d", "mod")

    # O(1)
    def __init__(self, lo, hi, mod=1000000007):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.mod = mod

    # O(logU) -- d[x] += v at offset x
    def _add(self, x, v):
        d, n, mod = self.d, self.n, self.mod
        x += 1
        while x <= n:
            d[x] = (d.get(x, 0) + v) % mod
            x += x & -x

    # O(logU) -- d[0] + ... + d[x] (0 for x = -1)
    def _prefix(self, x):
        d = self.d
        s = 0
        x += 1
        while x > 0:
            s += d.get(x, 0)
            x &= x - 1
        return s % self.mod

    # O(logU) -- a[i] += v (% MOD) for i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def rangeAddMod(self, l, r, v):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeAddMod: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if l > r:
            return
        self._add(l - self.lo, v)
        if r < self.hi:
            self._add(r + 1 - self.lo, -v)

    # O(logU) -- a[i], in [0, mod); needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        return self._prefix(i - self.lo) % self.mod

    # O(logU) -- a[i] += delta; needs lo <= i <= hi, else IndexError
    def pointAdd(self, i, delta):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAdd: needs lo <= i <= hi, got i = {i}")
        self.rangeAddMod(i, i, delta)

    # O(logU) -- a[i] = val; needs lo <= i <= hi, else IndexError
    def pointAssign(self, i, val):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointAssign: needs lo <= i <= hi, got i = {i}")
        self.rangeAddMod(i, i, val - self.pointGet(i))
