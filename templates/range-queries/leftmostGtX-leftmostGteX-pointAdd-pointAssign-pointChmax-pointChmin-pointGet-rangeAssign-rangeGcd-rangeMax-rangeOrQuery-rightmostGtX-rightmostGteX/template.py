# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeGcd-rangeMax-rangeOrQuery-rightmostGtX-rightmostGteX/template.py
# @operations: getAll leftmostGtX leftmostGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd rangeMax rangeOrQuery rightmostGtX rightmostGteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAssign: log(N)*log(U) ?
#   rangeGcd: log(N)+log(U) ?
#   rangeMax: log(N)
#   rangeOrQuery: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: mx[2*N] orr[2*N] g[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign) and range queries in
# O(logN); each node keeps its max, its OR, its gcd over its range. All indices 0-based, ranges inclusive [l, r];
# searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree
# of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied here, not yet to my
# children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both
# paths, each node redoing its own pending tag.
from math import gcd


INF, NEG = float("inf"), float("-inf")


class LazySegTree:
    __slots__ = ('n', 'h', 'mx', 'orr', 'g', 'asg', 'hasAsg')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mx = [0] * n + list(arr)
        self.orr = [0] * n + list(arr)
        self.g = [0] * n + list(arr)
        self.asg = [0] * n
        self.hasAsg = [0] * n
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            self._push(x)
        return [self._leaf(p) for p in range(n, 2 * n)]

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def leftmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                self._push(t)
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def leftmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                self._push(t)
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN * logU) -- a[i] += v
    def pointAdd(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = v
    def pointAssign(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = max(a[i], v)
    def pointChmax(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN * logU) -- a[i] = min(a[i], v)
    def pointChmin(self, i, v):
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]
    def pointGet(self, i):
        p = i + self.n
        self._pushPath(p)
        return self._leaf(p)

    # O(logN * logU) -- a[i] = v for i in [l, r]
    def rangeAssign(self, l, r, v):
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._applyAssign(lo, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAssign(hi, v)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|
    def rangeGcd(self, l, r):
        n, g = self.n, self.g
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res = gcd(res, g[lo])
                lo += 1
            if hi & 1:
                hi -= 1
                res = gcd(res, g[hi])
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        n, mx = self.n, self.mx
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    # O(logN) -- a[l] | ... | a[r]
    def rangeOrQuery(self, l, r):
        n, orr = self.n, self.orr
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    def rightmostGtX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    def rightmostGteX(self, l, r, x):
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.mx[p] = v
        self.orr[p] = v
        self.g[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.mx[p]

    def _pull(self, x):  # recompute node x from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        self.orr[x] = self.orr[a] | self.orr[b]
        self.g[x] = gcd(self.g[a], self.g[b])
        if self.hasAsg[x]:
            self._setAssign(x, self.asg[x])

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        while p > 1:
            p >>= 1
            self._pull(p)

    def _nodes(self, l, r):  # the O(logN) nodes covering a[l..r], left to right, each with its level
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    def _setAssign(self, x, v):  # every value under node x becomes v
        self.mx[x] = v
        self.orr[x] = v
        self.g[x] = v  # (read through a gcd: |v|)

    def _applyAssign(self, x, v):
        self._setAssign(x, v)
        if x < self.n:
            self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, v)
            self._applyAssign(b, v)
            self.hasAsg[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s)
