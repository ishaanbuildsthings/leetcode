# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/beats-sum-min-max-or-updates-div-mod-sqrt/template.py
# @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMin rangeMod rangeOrQuery rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: beats
# @complexities:
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeFloorDiv: log(N)*log(U) amortized
#   rangeFloorSqrt: log(N)*log(log(U)) amortized
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeMod: log(N)*log(U) amortized
#   rangeOrQuery: log(N)
#   rangeSum: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] mx[2*N] orr[2*N]
#   tags: none
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates

# Shrink segment tree with composable aggregates (2N iterative): range updates (rangeFloorDiv, rangeMod,
# rangeFloorSqrt; mod / floor div / floor sqrt walk down every node whose max still changes, and each value can only
# shrink O(logU) times) and range queries in O(logN); each node keeps its sum, its min, its max, its OR over its
# range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n);
# a node used by a query or update is a perfect subtree of 2^s leaves (s = its level); an update rewrites a leaf, then
# its ancestors.
from math import isqrt


INF, NEG = float("inf"), float("-inf")


class ShrinkSegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'mx', 'orr')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.orr = [0] * n + list(arr)
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def leftmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def leftmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def leftmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def leftmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- a[i] += v
    def pointAdd(self, i, v):
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        return self._leaf(p)

    # amortized O(logN * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing)
    def rangeFloorDiv(self, l, r, x):
        if x >= 2:
            self._shrinkRange(l, r, 1, lambda v: v // x)

    # amortized O(logN * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0)
    def rangeFloorSqrt(self, l, r):
        self._shrinkRange(l, r, 2, isqrt)

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        n, mx = self.n, self.mx
        res, lo, hi = NEG, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mx[lo] > res:
                    res = mx[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mx[hi] > res:
                    res = mx[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        n, mn = self.n, self.mn
        res, lo, hi = INF, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                if mn[lo] < res:
                    res = mn[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                if mn[hi] < res:
                    res = mn[hi]
            lo >>= 1
            hi >>= 1
        return res

    # amortized O(logN * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1)
    def rangeMod(self, l, r, x):
        if x >= 1:
            self._shrinkRange(l, r, x, lambda v: v % x)

    # O(logN) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        n, orr = self.n, self.orr
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res |= orr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res |= orr[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        n, sm = self.n, self.sm
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res += sm[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res += sm[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def rightmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def rightmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    def rightmostLtX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    def rightmostLteX(self, l, r, x):
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.orr[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x):  # recompute node x from its children
        a, b = 2 * x, 2 * x + 1
        self.sm[x] = self.sm[a] + self.sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        self.orr[x] = self.orr[a] | self.orr[b]

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        while p > 1:
            p >>= 1
            self._pull(p)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
        lo, hi, s, left, right = l + n, r + n + 1, 0, [], []
        while lo < hi:
            if lo & 1:
                left.append((lo, s))
                lo += 1
            if hi & 1:
                hi -= 1
                right.append((hi, s))
            lo >>= 1
            hi >>= 1
            s += 1
        return left + right[::-1]

    def _shrinkRange(self, l, r, lim, f):  # every value v >= lim in a[l..r] becomes f(v)
        n = self.n
        lo, hi, s = l + n, r + n + 1, 0
        while lo < hi:
            if lo & 1:
                self._shrink(lo, s, lim, f)
                lo += 1
            if hi & 1:
                hi -= 1
                self._shrink(hi, s, lim, f)
            lo >>= 1
            hi >>= 1
            s += 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    def _shrink(self, x, s, lim, f):  # every value v >= lim under node x (level s) becomes f(v) (the rest are fixed)
        if self.mx[x] < lim:
            return
        if x >= self.n:
            self._setLeaf(x, f(self.mx[x]))
            return
        self._shrink(2 * x, s - 1, lim, f)
        self._shrink(2 * x + 1, s - 1, lim, f)
        self._pull(x)
