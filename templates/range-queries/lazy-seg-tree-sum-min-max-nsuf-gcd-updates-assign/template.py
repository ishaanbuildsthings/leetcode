# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/lazy-seg-tree-sum-min-max-nsuf-gcd-updates-assign/template.py
# @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   leftmostGtX: log(N)
#   leftmostGteX: log(N)
#   leftmostLtX: log(N)
#   leftmostLteX: log(N)
#   minSuffixSum: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAssign: log(N)*log(U) ?
#   rangeGcd: log(N)+log(U) ?
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeSum: log(N)
#   rightmostGtX: log(N)
#   rightmostGteX: log(N)
#   rightmostLtX: log(N)
#   rightmostLteX: log(N)
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] mn[2*N] mx[2*N] nsuf[2*N] g[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign) and range queries in
# O(logN); each node keeps its sum, its min, its max, its min suffix sum, its gcd over its range. All indices 0-based,
# ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or
# update is a perfect subtree of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied
# here, not yet to my children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes,
# then rebuilds both paths, each node redoing its own pending tag.
from math import gcd


INF, NEG = float("inf"), float("-inf")


class LazySegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'mx', 'nsuf', 'g', 'asg', 'hasAsg')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.nsuf = [0] * n + list(arr)
        self.g = [0] * n + list(arr)
        self.asg = [0] * n
        self.hasAsg = [0] * n
        for x in range(n - 1, 0, -1):
            s, y = 0, x
            while y < n:  # (x's level: down its left edge to the leaves)
                y <<= 1
                s += 1
            self._pull(x, s)

    # O(N) -- the whole array, every pending tag pushed down on the way
    def getAll(self):
        n = self.n
        for x in range(1, n):  # (parents before children)
            s, y = 0, x
            while y < n:
                y <<= 1
                s += 1
            self._push(x, s)
        return [self._leaf(p) for p in range(n, 2 * n)]

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] > x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] >= x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] >= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in self._nodes(l, r):
            if F[t] < x:  # the first covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
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
                    self._push(t, s)
                    s -= 1
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

    # O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def minSuffixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minSuffixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, nsuf = self.sm, self.nsuf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = nsuf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + nsuf[t] < res:
                res = acc + nsuf[t]
            acc += sm[t]
        return res

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

    # O(logN * logU) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi, s = l + n, r + n + 1, 0
        while lo < hi:
            if lo & 1:
                self._applyAssign(lo, s, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAssign(hi, s, v)
            lo >>= 1
            hi >>= 1
            s += 1
        self._rebuild(l + n)
        self._rebuild(r + n)

    # O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm = self.n, self.sm
        self._pushPath(l + n)
        self._pushPath(r + n)
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

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] > x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] >= x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] >= x else 2 * t
                return t - n
        return -1

    # O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mn
        for t, s in reversed(self._nodes(l, r)):
            if F[t] < x:  # the last covering node with a passing value: walk down it
                while t < n:
                    self._push(t, s)
                    s -= 1
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
                    self._push(t, s)
                    s -= 1
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.nsuf[p] = v
        self.g[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        sm = self.sm
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        sm[x] = sm[a] + sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        self.g[x] = gcd(self.g[a], self.g[b])
        if self.hasAsg[x]:
            self._setAssign(x, s, self.asg[x])

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        s = 0
        while p > 1:
            p >>= 1
            s += 1
            self._pull(p, s)

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

    def _setAssign(self, x, s, v):  # every value under node x becomes v
        k = 1 << s
        self.sm[x] = v * k
        self.mn[x] = v
        self.mx[x] = v
        self.nsuf[x] = v * k if v < 0 else v
        self.g[x] = v  # (read through a gcd: |v|)

    def _applyAssign(self, x, s, v):
        self._setAssign(x, s, v)
        if x < self.n:
            self.asg[x], self.hasAsg[x] = v, 1

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        c = s - 1  # (their level)
        if self.hasAsg[x]:
            v = self.asg[x]
            self._applyAssign(a, c, v)
            self._applyAssign(b, c, v)
            self.hasAsg[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s, s)
