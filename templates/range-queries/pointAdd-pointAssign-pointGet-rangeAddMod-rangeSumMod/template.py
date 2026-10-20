# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeSumMod/template.py
# @operations: pointAdd pointAssign pointGet rangeAddMod rangeSumMod
# @data-structure-type: BIT
# @complexities:
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointGet: log(N)
#   rangeAddMod: log(N)
#   rangeSumMod: log(N)
#   build: N
# @memory:
#   layout: none
#   node: b1[1*N] b2[1*N]
#   tags: none
#   other: none
#   note: two Fenwick trees over the difference array d (d[i] = a[i] - a[i-1]): b1 over d[i], b2 over d[i] * i, all mod p

# Range add + range sum, everything mod p, with two Fenwick trees and no lazy tags. All indices 0-based, ranges
# inclusive [l, r]. a[0] + ... + a[x] = (x + 1) * sum(d[0..x]) - sum(d[i] * i for i in 0..x), d the difference array.
# Values are residues in [0, mod).


class RangeAddSumBITMod:
    __slots__ = ("n", "mod", "b1", "b2")

    # O(N)
    def __init__(self, arr, mod=1000000007):
        self.mod = mod
        n = self.n = len(arr)
        b1 = self.b1 = [0] * (n + 1)
        b2 = self.b2 = [0] * (n + 1)
        prev = 0
        for i, v in enumerate(arr):
            v %= mod
            d = (v - prev) % mod
            prev = v
            b1[i + 1] = d
            b2[i + 1] = d * i % mod
        for i in range(1, n + 1):
            j = i + (i & -i)
            if j <= n:
                b1[j] = (b1[j] + b1[i]) % mod
                b2[j] = (b2[j] + b2[i]) % mod

    def _addDiff(self, i, d):
        b1, b2, n, mod = self.b1, self.b2, self.n, self.mod
        d %= mod
        di = d * i % mod
        i += 1
        while i <= n:
            b1[i] = (b1[i] + d) % mod
            b2[i] = (b2[i] + di) % mod
            i += i & -i

    # O(logN) -- (a[0] + ... + a[x]) mod p (0 for x = -1)
    def _prefix(self, x):
        b1, b2 = self.b1, self.b2
        s1 = s2 = 0
        i = x + 1
        while i > 0:
            s1 += b1[i]
            s2 += b2[i]
            i &= i - 1
        return (s1 % self.mod * (x + 1) - s2) % self.mod

    # O(logN) -- a[i] += v (mod p) for i in [l, r]
    def rangeAddMod(self, l, r, v):
        if l > r:
            return
        self._addDiff(l, v)
        if r + 1 < self.n:
            self._addDiff(r + 1, -v)

    # O(logN) -- (a[l] + ... + a[r]) mod p
    def rangeSumMod(self, l, r):
        return (self._prefix(r) - self._prefix(l - 1)) % self.mod if l <= r else 0

    # O(logN) -- a[i], in [0, mod)
    def pointGet(self, i):
        return self.rangeSumMod(i, i)

    # O(logN) -- a[i] += delta (mod p)
    def pointAdd(self, i, delta):
        self.rangeAddMod(i, i, delta)

    # O(logN) -- a[i] = val (mod p)
    def pointAssign(self, i, val):
        self.rangeAddMod(i, i, val - self.pointGet(i))
