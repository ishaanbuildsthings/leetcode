# @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeGcd rangeLcm
# @data-structure-type: seg-tree
# @complexities:
#   pointAdd: ?
#   pointAssign: ?
#   pointChmax: ?
#   pointChmin: ?
#   pointGet: 1
#   rangeGcd: log(N)*log(U)
#   rangeLcm: ?
#   build: ?
# @memory:
#   layout: 2n-iterative
#   node: g[2*N] lcm[2*N]
#   tags: none
#   other: vals[1*N]
#   note: lcm values grow without bound (Python big ints; in C++ they overflow past 2^63), so lcm costs are unknown
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/GcdLcmSegmentTree.py

from math import gcd

# Range gcd + range lcm with point updates. All indices 0-based, ranges inclusive [l, r].
# Values may be negative or 0: gcd and lcm use absolute values, gcd(0, a) = a, lcm(0, a) = 0.
# Warning: lcm of a range can be astronomically large, so merging lcms gets slower as they grow.


def _lcm(a, b):
    if a == 0 or b == 0:
        return 0
    return a // gcd(a, b) * b


class GcdLcmTree:
    __slots__ = ("n", "vals", "g", "lcm")

    # O(N * cost of lcm)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.vals = list(arr)
        g = self.g = [0] * n + [abs(v) for v in arr]
        lcm = self.lcm = [0] * n + [abs(v) for v in arr]
        for i in range(n - 1, 0, -1):
            g[i] = gcd(g[2 * i], g[2 * i + 1])
            lcm[i] = _lcm(lcm[2 * i], lcm[2 * i + 1])

    # O(logN logU) -- gcd of a[l..r]
    def rangeGcd(self, l, r):
        g = self.g
        res = 0
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                res = gcd(res, g[l])
                l += 1
            if r & 1:
                r -= 1
                res = gcd(res, g[r])
            l >>= 1
            r >>= 1
        return res

    # lcm of a[l..r]
    def rangeLcm(self, l, r):
        lcm = self.lcm
        res = 1
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                res = _lcm(res, lcm[l])
                l += 1
            if r & 1:
                r -= 1
                res = _lcm(res, lcm[r])
            l >>= 1
            r >>= 1
        return res

    # a[i] = val
    def pointAssign(self, i, val):
        self.vals[i] = val
        g, lcm = self.g, self.lcm
        p = i + self.n
        g[p] = lcm[p] = abs(val)
        p >>= 1
        while p:
            g[p] = gcd(g[2 * p], g[2 * p + 1])
            lcm[p] = _lcm(lcm[2 * p], lcm[2 * p + 1])
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals[i]

    # a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.vals[i]:
            self.pointAssign(i, val)

    # a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.vals[i]:
            self.pointAssign(i, val)

    # a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.vals[i] + delta)
