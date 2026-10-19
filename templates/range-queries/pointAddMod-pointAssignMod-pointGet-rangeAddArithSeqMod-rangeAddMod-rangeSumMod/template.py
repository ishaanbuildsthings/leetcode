# @operations: pointAddMod pointAssignMod pointGet rangeAddArithSeqMod rangeAddMod rangeSumMod
# @data-structure-type: BIT
# @complexities:
#   pointAddMod: log(N)
#   pointAssignMod: log(N)
#   pointGet: log(N)
#   rangeAddArithSeqMod: log(N)
#   rangeAddMod: log(N)
#   rangeSumMod: log(N)
#   build: N
# @memory:
#   layout: none
#   node: bA[1*N] bB[1*N] bC[1*N]
#   tags: none
#   other: none
#   note: prefix sums are kept as A(x) + B(x) * x + C(x) * x(x+1)/2 mod p with A, B, C three Fenwick trees

# Range add of an arithmetic sequence (and plain range add) + range sum, all mod p, with three Fenwick trees.
# All indices 0-based, ranges inclusive [l, r]. Values are residues in [0, mod); start / step may be negative.
# Adding c0 + c1 * i to every i in [l, r] changes the prefix sum P(x) = a[0] + ... + a[x] by
#   x in [l, r]:  c0 * (x - l + 1) + c1 * (T(x) - T(l - 1))        T(k) = k * (k + 1) / 2
#   x > r:        the whole added total
# so keep P(x) = A(x) + B(x) * x + C(x) * T(x). T(x) is an integer before reducing mod p, so no division (or
# modular inverse of 2) is ever needed and any modulus works.


def _tri(k):
    return k * (k + 1) // 2


class ArithSeqSumBITMod:
    __slots__ = ("n", "mod", "bA", "bB", "bC")

    # O(N)
    def __init__(self, arr, mod=1000000007):
        self.mod = mod
        n = self.n = len(arr)
        bA = self.bA = [0] * (n + 1)
        self.bB = [0] * (n + 1)
        self.bC = [0] * (n + 1)
        for i, v in enumerate(arr):
            bA[i + 1] = v % mod
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                bA[j] = (bA[j] + bA[i]) % mod

    def _point(self, i, a, b, c):
        bA, bB, bC, n, mod = self.bA, self.bB, self.bC, self.n, self.mod
        a, b, c = a % mod, b % mod, c % mod
        i += 1
        while i <= n:
            bA[i] = (bA[i] + a) % mod
            bB[i] = (bB[i] + b) % mod
            bC[i] = (bC[i] + c) % mod
            i += i & -i

    # O(logN) -- (a[0] + ... + a[x]) mod p (0 for x = -1)
    def _prefix(self, x):
        bA, bB, bC, mod = self.bA, self.bB, self.bC, self.mod
        sa = sb = sc = 0
        i = x + 1
        while i > 0:
            sa += bA[i]
            sb += bB[i]
            sc += bC[i]
            i &= i - 1
        return (sa + sb % mod * x + sc % mod * (_tri(x) % mod)) % mod

    # O(logN) -- a[l + j] += start + j * step (mod p) for j in [0, r - l]
    def rangeAddArithSeqMod(self, l, r, start, step):
        if l > r:
            return
        c0, c1 = start - step * l, step  # adding c0 + c1 * i at index i
        a = c0 * (1 - l) - c1 * _tri(l - 1)
        self._point(l, a, c0, c1)
        if r + 1 < self.n:
            total = c0 * (r - l + 1) + c1 * (_tri(r) - _tri(l - 1))
            self._point(r + 1, total - a, -c0, -c1)

    # O(logN) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        self.rangeAddArithSeqMod(l, r, v, 0)

    # O(logN) -- (a[l] + ... + a[r]) mod p
    def rangeSumMod(self, l, r):
        return (self._prefix(r) - self._prefix(l - 1)) % self.mod if l <= r else 0

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        return self.rangeSumMod(i, i)

    # O(logN) -- a[i] += delta (mod p)
    def pointAddMod(self, i, delta):
        self.rangeAddMod(i, i, delta)

    # O(logN) -- a[i] = val (mod p)
    def pointAssignMod(self, i, val):
        self.rangeAddMod(i, i, val - self.pointGet(i))
