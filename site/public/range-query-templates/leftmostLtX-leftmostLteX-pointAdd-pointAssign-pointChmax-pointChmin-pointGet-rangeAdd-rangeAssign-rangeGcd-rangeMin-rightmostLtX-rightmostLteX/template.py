# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeGcd-rangeMin-rightmostLtX-rightmostLteX/template.py
# @operations: gcdAll getAll leftmostLtX leftmostLteX minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeGcd rangeMin rightmostLtX rightmostLteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAdd: log(N)*log(U) ?
#   rangeAssign: log(N)*log(U) ?
#   rangeGcd: log(N)+log(U) ?
#   rangeMin: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   minAll: log(N)
#   gcdAll: log(N)+log(U) ?
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: mn[2*N] g[2*N] fv[2*N] lv[2*N]
#   tags: asg[1*N] hasAsg[1*N] add[1*N]
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAdd, rangeAssign) and range queries
# in O(logN); each node keeps its min, its gcd over its range. All indices 0-based, ranges inclusive [l, r]; searches
# return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s
# leaves (s = its level), and every internal node holds its pending tags ("applied here, not yet to my children"): an
# update pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node
# redoing its own pending tag; a pending add or xor folds into a pending assign.
from math import gcd


INF, NEG = float("inf"), float("-inf")


class LazySegTree:
    __slots__ = ('n', 'h', 'mn', 'g', 'fv', 'lv', 'asg', 'hasAsg', 'add')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.mn = [0] * n + list(arr)
        self.g = [0] * n + [0] * n
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.asg = [0] * n
        self.hasAsg = [0] * n
        self.add = [0] * n
        for x in range(n - 1, 0, -1):
            self._pull(x)

    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            self._push(x)
        return [self._leaf(p) for p in range(n, 2 * n)]

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t if F[2 * t] < x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] <= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN * logU) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN * logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN * logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._pushPath(p)
        return self._leaf(p)

    # O(logN * logU) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi = l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                self._applyAdd(lo, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAdd(hi, v)
            lo >>= 1
            hi >>= 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN * logU) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        g, fv, lv = self.g, self.fv, self.lv
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, last = gcd(fv[t], g[t]), lv[t]  # the first value, then every adjacent difference
        for t, _ in ns[1:]:
            res = gcd(gcd(res, fv[t] - last), g[t])
            last = lv[t]
        return res

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, mn = self.n, self.mn
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] < x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] <= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t)
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.mn[p] = v
        self.g[p] = 0
        self.fv[p] = v
        self.lv[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.mn[p]

    def _pull(self, x):  # recompute node x from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        self.g[x] = gcd(gcd(self.g[a], self.g[b]), self.fv[b] - self.lv[a])  # (the adjacent differences)
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]
        if self.hasAsg[x]:
            self._setAssign(x, self.asg[x])
        elif self.add[x]:
            self._setAdd(x, self.add[x])

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
        self.mn[x] = v
        self.g[x] = 0
        self.fv[x] = self.lv[x] = v

    def _applyAssign(self, x, v):
        self._setAssign(x, v)
        if x < self.n:
            self.asg[x], self.hasAsg[x] = v, 1
            self.add[x] = 0

    def _setAdd(self, x, v):  # every value under node x gains v
        self.mn[x] += v
        self.fv[x] += v
        self.lv[x] += v

    def _applyAdd(self, x, v):
        self._setAdd(x, v)
        if x < self.n:
            if self.hasAsg[x]:
                self.asg[x] += v  # (still an assign, of a shifted value)
            else:
                self.add[x] += v

    def _push(self, x):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, v)
            self._applyAssign(b, v)
            self.hasAsg[x] = 0
        if self.add[x]:
            v = self.add[x]
            self._applyAdd(a, v)
            self._applyAdd(b, v)
            self.add[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s)
