# @operations: pointAdd pointAssign pointGet rangeAddMod rangeSumMod
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointGet: log(U)
#   rangeAddMod: log(U)
#   rangeSumMod: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: A[2*log(U)] B[2*log(U)]
#   tags: none
#   other: links[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; a range add changes two points of A and B. Python: a Fenwick tree in a dict (no links); C++: a dynamic prefix-sum tree in one shared node pool, call resetPool() between test cases

# Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by
#   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,
# so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes. All mod p.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseRangeAddSumBITMod:
    __slots__ = ("lo", "hi", "n", "d", "mod")

    # O(1)
    def __init__(self, lo, hi, mod=1000000007):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.mod = mod

    # O(logU) -- (A, B)[x] += (v0, v1) at offset x
    def _add(self, x, v0, v1):
        d, n, mod = self.d, self.n, self.mod
        v0 %= mod
        v1 %= mod
        x += 1
        while x <= n:
            e = d.get(x)
            if e is None:
                d[x] = [v0, v1]
            else:
                e[0] = (e[0] + v0) % mod
                e[1] = (e[1] + v1) % mod
            x += x & -x

    # O(logU) -- prefix sums of (A, B) over offsets 0..x (zeros for x = -1)
    def _prefix(self, x):
        d = self.d
        s0 = s1 = 0
        x += 1
        while x > 0:
            e = d.get(x)
            if e is not None:
                s0 += e[0]
                s1 += e[1]
            x &= x - 1
        mod = self.mod
        return s0 % mod, s1 % mod

    # O(logU) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        a = v * (1 - l)
        self._add(l, a, v)
        if r + 1 < self.n:
            self._add(r + 1, v * (r - l + 1) - a, -v)

    # O(logU) -- a[lo] + ... + a[lo + x] mod p (0 for x = -1)
    def _sum(self, x):
        sa, sb = self._prefix(x)
        return (sa + sb * x) % self.mod

    # O(logU) -- a[l] + ... + a[r] mod p
    def rangeSumMod(self, l, r):
        if l > r:
            return 0
        return (self._sum(r - self.lo) - self._sum(l - 1 - self.lo)) % self.mod

    # O(logU) -- a[i], in [0, mod)
    def pointGet(self, i):
        return self.rangeSumMod(i, i)

    # O(logU) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.rangeAddMod(i, i, delta)

    # O(logU) -- a[i] = val
    def pointAssign(self, i, val):
        self.rangeAddMod(i, i, val - self.pointGet(i))
