# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeGcd-rangeSum/template.py
# @operations: gcdAll getAll longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd rangeSum sumAll
# @data-structure-type: lazy-seg-tree
# @complexities:
#   getAll: N
#   longestEqualRun: log(N)
#   pointAdd: log(N)*log(U) ?
#   pointAssign: log(N)*log(U) ?
#   pointChmax: log(N)*log(U) ?
#   pointChmin: log(N)*log(U) ?
#   pointGet: log(N)
#   rangeAdd: log(N)*log(U) ?
#   rangeGcd: log(N)+log(U) ?
#   rangeSum: log(N)
#   sumAll: log(N)
#   gcdAll: log(N)+log(U) ?
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] g[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
#   tags: add[1*N]
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAdd) and range queries in O(logN);
# each node keeps its sum, its gcd, its first / last value and the equal runs at its ends and inside over its range.
# All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node
# used by a query or update is a perfect subtree of 2^s leaves (s = its level), and every internal node holds its
# pending tags ("applied here, not yet to my children"): an update pushes the tags on its two boundary leaf paths,
# tags the covering nodes, then rebuilds both paths, each node redoing its own pending tag.
from math import gcd


class LazySegTree:
    __slots__ = ('n', 'h', 'sm', 'g', 'fv', 'lv', 'pr', 'sr', 'br', 'add')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.g = [0] * n + [0] * n
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.pr = [0] * n + [1] * n
        self.sr = [0] * n + [1] * n
        self.br = [0] * n + [1] * n
        self.add = [0] * n
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

    # O(logN) -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def longestEqualRun(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"longestEqualRun: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        pr, sr, br, fv, lv = self.pr, self.sr, self.br, self.fv, self.lv
        ns = self._nodes(l, r)
        t, s = ns[0]
        p, q, res, k, last = pr[t], sr[t], br[t], 1 << s, lv[t]  # (prefix run, suffix run, best, length, last value)
        for t, s in ns[1:]:
            j = last == fv[t]
            if j and q + pr[t] > res:
                res = q + pr[t]
            if br[t] > res:
                res = br[t]
            if j and p == k:
                p += pr[t]
            q = q + sr[t] if j and sr[t] == 1 << s else sr[t]
            k += 1 << s
            last = lv[t]
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

    # O(logN * logU) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = self.n
        self._pushPath(l + n)
        self._pushPath(r + n)
        lo, hi, s = l + n, r + n + 1, 0
        while lo < hi:
            if lo & 1:
                self._applyAdd(lo, s, v)
                lo += 1
            if hi & 1:
                hi -= 1
                self._applyAdd(hi, s, v)
            lo >>= 1
            hi >>= 1
            s += 1
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

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.g[p] = 0
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        self.sm[x] = self.sm[a] + self.sm[b]
        self.g[x] = gcd(gcd(self.g[a], self.g[b]), self.fv[b] - self.lv[a])  # (the adjacent differences)
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]
        if self.add[x]:
            self._setAdd(x, s, self.add[x])

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

    def _setAdd(self, x, s, v):  # every value under node x gains v
        self.sm[x] += v << s
        self.fv[x] += v
        self.lv[x] += v

    def _applyAdd(self, x, s, v):
        self._setAdd(x, s, v)
        if x < self.n:
            self.add[x] += v

    def _push(self, x, s):  # hand node x's pending tags to its children
        a, b = 2 * x, 2 * x + 1
        c = s - 1  # (their level)
        if self.add[x]:
            v = self.add[x]
            self._applyAdd(a, c, v)
            self._applyAdd(b, c, v)
            self.add[x] = 0

    def _pushPath(self, p):  # hand down every pending tag on the path from the root to leaf p
        for s in range(self.h, 0, -1):
            self._push(p >> s, s)
