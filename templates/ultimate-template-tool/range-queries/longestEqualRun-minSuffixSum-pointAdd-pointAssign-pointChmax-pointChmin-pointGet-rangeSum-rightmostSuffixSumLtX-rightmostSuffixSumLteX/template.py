# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/longestEqualRun-minSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumLtX-rightmostSuffixSumLteX/template.py
# @operations: getAll longestEqualRun minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum rightmostSuffixSumLtX rightmostSuffixSumLteX sumAll
# @data-structure-type: seg-tree
# @letters: same
# @complexities:
#   getAll: N
#   longestEqualRun: log(N)
#   minSuffixSum: log(N)
#   pointAdd: log(N)
#   pointAssign: log(N)
#   pointChmax: log(N)
#   pointChmin: log(N)
#   pointGet: log(N)
#   rangeSum: log(N)
#   rightmostSuffixSumLtX: log(N)
#   rightmostSuffixSumLteX: log(N)
#   sumAll: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] nsuf[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
#   tags: none
#   other: none
#   note: leaves [n, 2n) hold each value's own aggregates

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its sum, its min suffix sum, its first / last value and the equal runs at its ends and inside over its range. All
# indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used
# by a query or update is a perfect subtree of 2^s leaves (s = its level); an update rewrites a leaf, then its
# ancestors.

class SegTree:
    __slots__ = ('n', 'h', 'sm', 'nsuf', 'fv', 'lv', 'pr', 'sr', 'br')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.nsuf = [0] * n + list(arr)
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.pr = [0] * n + [1] * n
        self.sr = [0] * n + [1] * n
        self.br = [0] * n + [1] * n
        for x in range(n - 1, 0, -1):
            s, y = 0, x
            while y < n:  # (x's level: down its left edge to the leaves)
                y <<= 1
                s += 1
            self._pull(x, s)

    # O(N) -- the whole array
    def getAll(self):
        return self.sm[self.n:]

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

    # O(logN) -- a[i] += v; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, self._leaf(p) + v)
        self._rebuild(p)

    # O(logN) -- a[i] = v; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, v)
        self._rebuild(p)

    # O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, max(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._setLeaf(p, min(self._leaf(p), v))
        self._rebuild(p)

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        return self._leaf(p)

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] < x, or -1 (a walk pruned by min suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.nsuf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] < x:
                while t < n:
                    if acc + P[2 * t + 1] < x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] <= x, or -1 (a walk pruned by min suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.nsuf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] <= x:
                while t < n:
                    if acc + P[2 * t + 1] <= x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.nsuf[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = 2 * x, 2 * x + 1
        sm = self.sm
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        sm[x] = sm[a] + sm[b]
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]

    def _rebuild(self, p):  # recompute every ancestor of leaf p
        s = 0
        while p > 1:
            p >>= 1
            s += 1
            self._pull(p, s)

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
