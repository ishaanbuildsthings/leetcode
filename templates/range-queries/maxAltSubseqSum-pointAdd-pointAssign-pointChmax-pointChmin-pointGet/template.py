# @operations: maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet
# @data-structure-type: seg-tree
# @complexities:
#   maxAltSubseqSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: 1
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: pp[2*N] pm[2*N] mp[2*N] mm[2*N]
#   tags: none
#   other: vals[1*N]
#   note: f[s][e] = best alternating sum inside the node that starts with sign s and ends with sign e; queries fold a left and a right accumulator

# Max alternating subsequence sum  +a[i1] - a[i2] + a[i3] - ...  (i1 < i2 < ..., non-empty, starts with +) inside
# a[l..r], with point updates. All indices 0-based, ranges inclusive.
# Each node keeps the best sum for each (first sign, last sign) pair. Joining A then B either takes one side alone
# or glues A's piece ending in sign x to B's piece starting with the opposite sign. Not commutative, so a query
# folds a left and a right accumulator.

NEG = float("-inf")


class AltSumTree:
    __slots__ = ("n", "vals", "pp", "pm", "mp", "mm")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.vals = list(arr)
        self.pp = [NEG] * n + list(arr)          # starts +, ends +
        self.pm = [NEG] * (2 * n)                # starts +, ends -
        self.mp = [NEG] * (2 * n)                # starts -, ends +
        self.mm = [NEG] * n + [-v for v in arr]  # starts -, ends -
        for x in range(n - 1, 0, -1):
            self._pull(x)

    @staticmethod
    def _merge(a, b):
        app, apm, amp, amm = a
        bpp, bpm, bmp, bmm = b
        return (max(app, bpp, app + bmp, apm + bpp),
                max(apm, bpm, app + bmm, apm + bpm),
                max(amp, bmp, amp + bmp, amm + bpp),
                max(amm, bmm, amp + bmm, amm + bpm))

    def _node(self, x):
        return self.pp[x], self.pm[x], self.mp[x], self.mm[x]

    def _pull(self, x):
        self.pp[x], self.pm[x], self.mp[x], self.mm[x] = self._merge(self._node(2 * x), self._node(2 * x + 1))

    # O(logN) -- max over non-empty subsequences of a[l..r] of +first - second + third - ...
    def maxAltSubseqSum(self, l, r):
        left = right = None
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                left = self._node(l) if left is None else self._merge(left, self._node(l))
                l += 1
            if r & 1:
                r -= 1
                right = self._node(r) if right is None else self._merge(self._node(r), right)
            l >>= 1
            r >>= 1
        res = right if left is None else left if right is None else self._merge(left, right)
        return max(res[0], res[1])

    # O(logN) -- a[i] = val
    def pointAssign(self, i, val):
        self.vals[i] = val
        p = i + self.n
        self.pp[p], self.pm[p], self.mp[p], self.mm[p] = val, NEG, NEG, -val
        p >>= 1
        while p:
            self._pull(p)
            p >>= 1

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.vals[i]

    # O(logN) -- a[i] += delta
    def pointAdd(self, i, delta):
        self.pointAssign(i, self.vals[i] + delta)

    # O(logN) -- a[i] = max(a[i], val)
    def pointChmax(self, i, val):
        if val > self.vals[i]:
            self.pointAssign(i, val)

    # O(logN) -- a[i] = min(a[i], val)
    def pointChmin(self, i, val):
        if val < self.vals[i]:
            self.pointAssign(i, val)
