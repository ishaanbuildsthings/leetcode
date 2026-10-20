# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddArithSeqMod-rangeAddMod-rangeSumMod/sparse.py
# @operations: pointAdd pointAssign pointGet rangeAddArithSeqMod rangeAddMod rangeSumMod
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(U)
#   pointAssign: log(U)
#   pointGet: log(U)
#   rangeAddArithSeqMod: log(U)
#   rangeAddMod: log(U)
#   rangeSumMod: log(U)
#   build: 1
# @memory:
#   layout: sparse
#   node: A[2*log(U)] B[2*log(U)] C[2*log(U)]
#   tags: none
#   other: children[4*log(U)]
#   note: per update, the O(logU) entries above each changed position; an arithmetic-sequence add changes two points of A, B and C. A Fenwick tree in a dict (no child pointers)


def _tri(k):
    return k * (k + 1) // 2

# Range add of an arithmetic sequence (and plain range add) + range sum, all mod p. Adding c0 + c1 * x (x = i - lo)
# on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[lo + x] by c0 * (x - l + 1) + c1 * (tri(x) - tri(l - 1))
# for x in [l, r] (tri(k) = k(k+1)/2), and by the whole added total past r. So P(x) = A(x) + B(x) * x +
# C(x) * tri(x) with A, B, C prefix sums of point changes; tri keeps every coefficient an integer.
# Over any index range [lo, hi] (huge or negative is fine); every position starts at 0. Sparse: a Fenwick tree in a
# dict keyed by offset x = i - lo, so only the O(logU) entries above changed positions exist.


class SparseArithSeqSumBITMod:
    __slots__ = ("lo", "hi", "n", "d", "mod")

    # O(1)
    def __init__(self, lo, hi, mod=1000000007):
        self.lo, self.hi = lo, hi
        self.n = hi - lo + 1
        self.d = {}
        self.mod = mod

    # O(logU) -- (A, B, C)[x] += (v0, v1, v2) at offset x
    def _add(self, x, v0, v1, v2):
        d, n, mod = self.d, self.n, self.mod
        v0 %= mod
        v1 %= mod
        v2 %= mod
        x += 1
        while x <= n:
            e = d.get(x)
            if e is None:
                d[x] = [v0, v1, v2]
            else:
                e[0] = (e[0] + v0) % mod
                e[1] = (e[1] + v1) % mod
                e[2] = (e[2] + v2) % mod
            x += x & -x

    # O(logU) -- prefix sums of (A, B, C) over offsets 0..x (zeros for x = -1)
    def _prefix(self, x):
        d = self.d
        s0 = s1 = s2 = 0
        x += 1
        while x > 0:
            e = d.get(x)
            if e is not None:
                s0 += e[0]
                s1 += e[1]
                s2 += e[2]
            x &= x - 1
        mod = self.mod
        return s0 % mod, s1 % mod, s2 % mod

    # O(logU) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    def rangeAddArithSeqMod(self, l, r, start, step):
        if l > r:
            return
        l -= self.lo
        r -= self.lo
        c0, c1 = start - step * l, step  # adding c0 + c1 * x at offset x
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._add(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._add(r + 1, total - a, -c0, -c1)

    # O(logU) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        self.rangeAddArithSeqMod(l, r, v, 0)

    # O(logU) -- a[lo] + ... + a[lo + x] mod p (0 for x = -1)
    def _sum(self, x):
        sa, sb, sc = self._prefix(x)
        return (sa + sb * x + sc * _tri(x)) % self.mod

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
