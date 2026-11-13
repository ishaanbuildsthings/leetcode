# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/edge-lazy-seg-tree-sum-pre-suf-best-npre-nsuf-nbest-xor-and-or-gcd-run-alt-updates-assign/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/lazy-seg-tree-sum-pre-suf-best-npre-nsuf-nbest-xor-and-or-gcd-run-alt-updates-assign/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathAND edgePathAssign edgePathFirstPrefixSumGtX edgePathFirstPrefixSumGteX edgePathFirstPrefixSumLtX edgePathFirstPrefixSumLteX edgePathGcd edgePathLastSuffixSumGtX edgePathLastSuffixSumGteX edgePathLastSuffixSumLtX edgePathLastSuffixSumLteX edgePathMaxPrefixSum edgePathMaxSubarraySum edgePathMaxSuffixSum edgePathMinPrefixSum edgePathMinSubarraySum edgePathMinSuffixSum edgePathOR edgePathSum edgePathXOR edgeSubtreeAND edgeSubtreeAssign edgeSubtreeGcd edgeSubtreeOR edgeSubtreeSum edgeSubtreeXOR isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: lazy-seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)*log(U) ?
#   edgeAssign: log(N)*log(U) ?
#   edgeChmax: log(N)*log(U) ?
#   edgeChmin: log(N)*log(U) ?
#   edgeGet: log(N)
#   edgePathAND: log^2(N)
#   edgePathAssign: log^2(N)*log(U) ?
#   edgePathFirstPrefixSumGtX: log^2(N)
#   edgePathFirstPrefixSumGteX: log^2(N)
#   edgePathFirstPrefixSumLtX: log^2(N)
#   edgePathFirstPrefixSumLteX: log^2(N)
#   edgePathGcd: log^2(N)+log(U)*log(N) ?
#   edgePathLastSuffixSumGtX: log^2(N)
#   edgePathLastSuffixSumGteX: log^2(N)
#   edgePathLastSuffixSumLtX: log^2(N)
#   edgePathLastSuffixSumLteX: log^2(N)
#   edgePathMaxPrefixSum: log^2(N)
#   edgePathMaxSubarraySum: log^2(N)
#   edgePathMaxSuffixSum: log^2(N)
#   edgePathMinPrefixSum: log^2(N)
#   edgePathMinSubarraySum: log^2(N)
#   edgePathMinSuffixSum: log^2(N)
#   edgePathOR: log^2(N)
#   edgePathSum: log^2(N)
#   edgePathXOR: log^2(N)
#   edgeSubtreeAND: log(N)
#   edgeSubtreeAssign: log(N)*log(U) ?
#   edgeSubtreeGcd: log(N)+log(U) ?
#   edgeSubtreeOR: log(N)
#   edgeSubtreeSum: log(N)
#   edgeSubtreeXOR: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(U) ?
# @memory:
#   layout: 2n-iterative
#   node: sm[2*N] pre[2*N] suf[2*N] best[2*N] npre[2*N] nsuf[2*N] nbest[2*N] xr[2*N] an[2*N] orr[2*N] g[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N] a00[2*N] a01[2*N] a10[2*N] a11[2*N]
#   tags: asg[1*N] hasAsg[1*N]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

# Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign) and range queries in
# O(logN); each node keeps its sum, its best prefix sum, its best suffix sum, its best subarray sum, its min prefix
# sum, its min suffix sum, its min subarray sum, its xor, its AND, its OR, its gcd, its first / last value and the
# equal runs at its ends and inside, its best alternating (+ - + ...) subsequence sum for each start / end sign over
# its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies. Leaves
# tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level), and every internal
# node holds its pending tags ("applied here, not yet to my children"): an update pushes the tags on its two boundary
# leaf paths, tags the covering nodes, then rebuilds both paths, each node redoing its own pending tag.
from math import gcd


INF, NEG = float("inf"), float("-inf")


def _altJoin(A, B):  # A's part, then B's: (++, +-, -+, --) = best by (start sign, end sign)
    a0, a1, a2, a3 = A
    b0, b1, b2, b3 = B
    return (max(a0, b0, a0 + b2, a1 + b0), max(a1, b1, a0 + b3, a1 + b1),
            max(a2, b2, a2 + b2, a3 + b0), max(a3, b3, a2 + b3, a3 + b1))


class LazySegTree:
    __slots__ = ('n', 'h', 'sm', 'pre', 'suf', 'best', 'npre', 'nsuf', 'nbest', 'xr', 'an', 'orr', 'g', 'fv', 'lv',
                 'pr', 'sr', 'br', 'a00', 'a01', 'a10', 'a11', 'asg', 'hasAsg')


    # O(N log U) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.pre = [0] * n + list(arr)
        self.suf = [0] * n + list(arr)
        self.best = [0] * n + list(arr)
        self.npre = [0] * n + list(arr)
        self.nsuf = [0] * n + list(arr)
        self.nbest = [0] * n + list(arr)
        self.xr = [0] * n + list(arr)
        self.an = [0] * n + list(arr)
        self.orr = [0] * n + list(arr)
        self.g = [0] * n + list(arr)
        self.fv = [0] * n + list(arr)
        self.lv = [0] * n + list(arr)
        self.pr = [0] * n + [1] * n
        self.sr = [0] * n + [1] * n
        self.br = [0] * n + [1] * n
        self.a00 = [0] * n + list(arr)
        self.a01 = [0] * n + [NEG] * n
        self.a10 = [0] * n + [NEG] * n
        self.a11 = [0] * n + [-v for v in arr]
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

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.pre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] > x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t] > x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.pre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] >= x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t] >= x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.npre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] < x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t] < x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums); needs
    # 0 <= l <= r < n, else IndexError
    def leftmostPrefixSumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostPrefixSumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.npre
        acc = 0
        for t, s in self._nodes(l, r):
            if acc + P[t] <= x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t] <= x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

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

    # O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs 0 <= l <= r < n, else
    # IndexError
    def maxAltSubseqSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxAltSubseqSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        a00, a01, a10, a11 = self.a00, self.a01, self.a10, self.a11
        ns = self._nodes(l, r)
        t = ns[0][0]
        c = (a00[t], a01[t], a10[t], a11[t])
        for t, _ in ns[1:]:
            c = _altJoin(c, (a00[t], a01[t], a10[t], a11[t]))
        return max(c[0], c[1])

    # O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def maxPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, pre = self.sm, self.pre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = pre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + pre[t] > res:
                res = acc + pre[t]
            acc += sm[t]
        return res

    # O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def maxSubarraySum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSubarraySum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, pre, suf, best = self.sm, self.pre, self.suf, self.best
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = best[t], suf[t]  # (q: the best sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = max(res, best[t], q + pre[t])
            q = max(suf[t], sm[t] + q)
        return res

    # O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def maxSuffixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"maxSuffixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, suf = self.sm, self.suf
        ns = self._nodes(l, r)
        t = ns[-1][0]
        res, acc = suf[t], sm[t]
        for t, _ in reversed(ns[:-1]):
            if acc + suf[t] > res:
                res = acc + suf[t]
            acc += sm[t]
        return res

    # O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def minPrefixSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minPrefixSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, npre = self.sm, self.npre
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, acc = npre[t], sm[t]
        for t, _ in ns[1:]:
            if acc + npre[t] < res:
                res = acc + npre[t]
            acc += sm[t]
        return res

    # O(logN) -- min sum of a non-empty contiguous subarray of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def minSubarraySum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"minSubarraySum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        sm, npre, nsuf, nbest = self.sm, self.npre, self.nsuf, self.nbest
        ns = self._nodes(l, r)
        t = ns[0][0]
        res, q = nbest[t], nsuf[t]  # (q: the min sum ending at the right edge so far)
        for t, _ in ns[1:]:
            res = min(res, nbest[t], q + npre[t])
            q = min(nsuf[t], sm[t] + q)
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

    # O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, an = self.n, self.an
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = -1, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res &= an[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res &= an[hi]
            lo >>= 1
            hi >>= 1
        return res

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

    # O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeXorQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, xr = self.n, self.xr
        self._pushPath(l + n)
        self._pushPath(r + n)
        res, lo, hi = 0, l + n, r + n + 1
        while lo < hi:
            if lo & 1:
                res ^= xr[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res ^= xr[hi]
            lo >>= 1
            hi >>= 1
        return res

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.suf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] > x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t + 1] > x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums); needs
    # 0 <= l <= r < n, else IndexError
    def rightmostSuffixSumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostSuffixSumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, sm, P = self.n, self.sm, self.suf
        acc = 0
        for t, s in reversed(self._nodes(l, r)):
            if acc + P[t] >= x:
                while t < n:
                    self._push(t, s)
                    s -= 1
                    if acc + P[2 * t + 1] >= x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

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
                    self._push(t, s)
                    s -= 1
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
                    self._push(t, s)
                    s -= 1
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

    # O(log(N)+log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)

    # O(log(N)) -- xor of the whole array a[0..n-1] (rangeXorQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def xorAll(self):
        if self.n < 1:
            raise IndexError("xorAll: needs n >= 1")
        return self.rangeXorQuery(0, self.n - 1)

    # O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.pre[p] = v
        self.suf[p] = v
        self.best[p] = v
        self.npre[p] = v
        self.nsuf[p] = v
        self.nbest[p] = v
        self.xr[p] = v
        self.an[p] = v
        self.orr[p] = v
        self.g[p] = v
        self.fv[p] = v
        self.lv[p] = v
        self.pr[p] = 1
        self.sr[p] = 1
        self.br[p] = 1
        self.a00[p] = v
        self.a01[p] = NEG
        self.a10[p] = NEG
        self.a11[p] = -v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children, then redo its own pending tags
        a, b = 2 * x, 2 * x + 1
        sm = self.sm
        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])
        self.npre[x] = min(self.npre[a], sm[a] + self.npre[b])
        self.nsuf[x] = min(self.nsuf[b], sm[b] + self.nsuf[a])
        self.nbest[x] = min(self.nbest[a], self.nbest[b], self.nsuf[a] + self.npre[b])
        sm[x] = sm[a] + sm[b]
        self.xr[x] = self.xr[a] ^ self.xr[b]
        self.an[x] = self.an[a] & self.an[b]
        self.orr[x] = self.orr[a] | self.orr[b]
        self.g[x] = gcd(self.g[a], self.g[b])
        h, j = 1 << (s - 1), self.lv[a] == self.fv[b]
        pa, sb = self.pr[a], self.sr[b]
        self.br[x] = max(self.br[a], self.br[b], self.sr[a] + self.pr[b] if j else 0)
        self.pr[x] = pa + self.pr[b] if j and pa == h else pa
        self.sr[x] = sb + self.sr[a] if j and sb == h else sb
        self.fv[x] = self.fv[a]
        self.lv[x] = self.lv[b]
        A = (self.a00[a], self.a01[a], self.a10[a], self.a11[a])
        B = (self.a00[b], self.a01[b], self.a10[b], self.a11[b])
        self.a00[x], self.a01[x], self.a10[x], self.a11[x] = _altJoin(A, B)
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
        self.an[x] = v
        self.orr[x] = v
        self.pre[x] = self.suf[x] = self.best[x] = v * k if v > 0 else v
        self.npre[x] = self.nsuf[x] = self.nbest[x] = v * k if v < 0 else v
        self.xr[x] = v if k & 1 else 0
        self.g[x] = v  # (read through a gcd: |v|)
        self.fv[x] = self.lv[x] = v
        self.pr[x] = self.sr[x] = self.br[x] = k
        self.a00[x], self.a11[x] = v, -v
        self.a01[x] = self.a10[x] = 0 if k > 1 else NEG

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


from bisect import bisect_left
from math import gcd


# tree = Tree(edges, root)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0)    # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1)    # nodes 1..3, rooted at 1
#
# An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
# between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the end
# farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns. Nodes
# go in and come out with your labels, -1 means "none", and a label that is not in the tree raises IndexError. Nothing
# recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Each edge's weight sits at its lower end's position in
# the range structure above (LazySegTree); the root's position holds no edge. The edges below node are one range of it,
# and the edges of a path a..b are O(log n) ranges, one per chain it crosses.
class Tree:
    # O(n * log U) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or an edge has no weight
    def __init__(self, edges, root):
        n = len(edges) + 1
        lo = float("inf")
        for e in edges:
            if len(e) != 2 and len(e) != 3:
                raise ValueError(f"Tree: every edge needs 2 or 3 numbers, (a, b) or (a, b, w), got {e}")
            if e[0] < lo:
                lo = e[0]
            if e[1] < lo:
                lo = e[1]
        if not edges:
            lo = root
        if lo != 0 and lo != 1:
            raise ValueError(f"Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is {lo}")
        hi = lo + n - 1
        if not lo <= root <= hi:
            raise ValueError(f"Tree: root must be one of the nodes {lo}..{hi}, got {root}")
        adj = [[] for _ in range(hi + 1)]
        for e in edges:
            a, b = e[0], e[1]
            if a > hi or b > hi:
                raise ValueError(f"Tree: {n - 1} edges means the nodes are {lo}..{hi}, got the edge ({a}, {b})")
            adj[a].append(b)
            adj[b].append(a)

        # parents and depths, top down (par is -2 until a node is reached)
        par = [-2] * (hi + 1)
        dep = [0] * (hi + 1)
        par[root] = -1
        bfs = [root]
        for v in bfs:
            d = dep[v] + 1
            for u in adj[v]:
                if par[u] == -2:
                    par[u] = v
                    dep[u] = d
                    bfs.append(u)
        if len(bfs) != n:
            raise ValueError("Tree: the edges do not form one tree (some node cannot be reached from root)")

        # subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz = [1] * (hi + 1)
        for i in range(n - 1, 0, -1):
            v = bfs[i]
            sz[par[v]] += sz[v]
        heavy = [-1] * (hi + 1)
        for i in range(1, n):
            v = bfs[i]
            p = par[v]
            if heavy[p] == -1 or sz[v] > sz[heavy[p]]:
                heavy[p] = v

        # positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head = [0] * (hi + 1)  # the top node of each node's chain
        pos = [0] * (hi + 1)
        order = [0] * n  # order[pos[v]] = v
        head[root] = root
        stack = [root]
        t = 0
        while stack:
            v = stack.pop()
            pos[v] = t
            order[t] = v
            t += 1
            h = heavy[v]
            p = par[v]
            for u in adj[v]:
                if u != p and u != h:
                    head[u] = u
                    stack.append(u)
            if h != -1:  # pushed last, so it is popped next
                head[h] = head[v]
                stack.append(h)

        # depthPos[depthStart[d] : depthStart[d + 1]] = the positions of the nodes at depth d, increasing
        maxDep = dep[bfs[-1]]
        depthStart = [0] * (maxDep + 2)
        for v in bfs:
            depthStart[dep[v] + 1] += 1
        for d in range(maxDep + 1):
            depthStart[d + 1] += depthStart[d]
        at = depthStart[:]
        depthPos = [0] * n
        for i in range(n):
            d = dep[order[i]]
            depthPos[at[d]] = i
            at[d] += 1

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        arr = [edges[0][2] if edges else 0] * n  # (position 0 is the root's: it holds no edge, never read)
        for e in edges:
            a, b = e[0], e[1]
            arr[pos[a] if par[a] == b else pos[b]] = e[2]
        self.seg = LazySegTree(arr)  # each edge's weight, at its lower end's position

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.seg.pointGet(self._edge("edgeGet", a, b))

    # O(log n * log U) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.seg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log n * log U) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        self.seg.pointAdd(self._edge("edgeAdd", a, b), w)

    # O(log n * log U) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        self.seg.pointChmax(self._edge("edgeChmax", a, b), w)

    # O(log n * log U) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        self.seg.pointChmin(self._edge("edgeChmin", a, b), w)

    # O(log^2 n * log U) -- weight = w for every edge on the path a..b
    def edgePathAssign(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAssign", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.rangeAssign
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], w)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, w) if l < r else apply(r + 1, l, w)

    # O(log^2 n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeSum
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r)
        return res

    # O(log^2 n + log U * log n) -- gcd of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathGcd(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathGcd", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeGcd
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res = gcd(res, query(pos[head[a]], pos[a]))
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res = gcd(res, query(l + 1, r))
        return res

    # O(log^2 n) -- xor of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathXOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathXOR", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeXorQuery
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res ^= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res ^= query(l + 1, r)
        return res

    # O(log^2 n) -- AND of the edge weights on the path a..b; -1 (every bit set) when a == b (no edges)
    def edgePathAND(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAND", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeAndQuery
        res = -1
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res &= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res &= query(l + 1, r)
        return res

    # O(log^2 n) -- OR of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathOR", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeOrQuery
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res |= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res |= query(l + 1, r)
        return res

    # O(log^2 n) -- max sum of a non-empty stretch of the path a..b; -inf when a == b (no edges)
    def edgePathMaxSubarraySum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMaxSubarraySum", a, b)
        head, par, dep, pos, seg = self.head, self.par, self.dep, self.pos, self.seg
        total, starting, ending, inside = seg.rangeSum, seg.maxPrefixSum, seg.maxSuffixSum, seg.maxSubarraySum
        best = tail = float("-inf")  # the best stretch so far; the best one ending at the last edge walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                s, inner = total(l, r), inside(l, r)
                if inner > best:
                    best = inner
                v = tail + ending(l, r)
                if v > best:
                    best = v
                v = starting(l, r)
                tail = v if v > tail + s else tail + s
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            s, inner = total(l, r), inside(l, r)
            if inner > best:
                best = inner
            v = tail + ending(l, r)
            if v > best:
                best = v
            v = starting(l, r)
            tail = v if v > tail + s else tail + s
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            s, inner = total(l, r), inside(l, r)
            if inner > best:
                best = inner
            v = tail + starting(l, r)
            if v > best:
                best = v
            v = ending(l, r)
            tail = v if v > tail + s else tail + s
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            s, inner = total(l, r), inside(l, r)
            if inner > best:
                best = inner
            v = tail + starting(l, r)
            if v > best:
                best = v
            v = ending(l, r)
            tail = v if v > tail + s else tail + s
        return best

    # O(log^2 n) -- min sum of a non-empty stretch of the path a..b; inf when a == b (no edges)
    def edgePathMinSubarraySum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMinSubarraySum", a, b)
        head, par, dep, pos, seg = self.head, self.par, self.dep, self.pos, self.seg
        total, starting, ending, inside = seg.rangeSum, seg.minPrefixSum, seg.minSuffixSum, seg.minSubarraySum
        best = tail = float("inf")  # the best stretch so far; the best one ending at the last edge walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                s, inner = total(l, r), inside(l, r)
                if inner < best:
                    best = inner
                v = tail + ending(l, r)
                if v < best:
                    best = v
                v = starting(l, r)
                tail = v if v < tail + s else tail + s
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            s, inner = total(l, r), inside(l, r)
            if inner < best:
                best = inner
            v = tail + ending(l, r)
            if v < best:
                best = v
            v = starting(l, r)
            tail = v if v < tail + s else tail + s
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            s, inner = total(l, r), inside(l, r)
            if inner < best:
                best = inner
            v = tail + starting(l, r)
            if v < best:
                best = v
            v = ending(l, r)
            tail = v if v < tail + s else tail + s
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            s, inner = total(l, r), inside(l, r)
            if inner < best:
                best = inner
            v = tail + starting(l, r)
            if v < best:
                best = v
            v = ending(l, r)
            tail = v if v < tail + s else tail + s
        return best

    def _maxPrefixSum(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        starting, ending, total = self.seg.maxPrefixSum, self.seg.maxSuffixSum, self.seg.rangeSum
        run, best = 0, float("-inf")  # the sum of the pieces already walked; the best prefix so far
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                v = run + ending(l, r)
                if v > best:
                    best = v
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            v = run + ending(l, r)
            if v > best:
                best = v
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            v = run + starting(l, r)
            if v > best:
                best = v
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            v = run + starting(l, r)
            if v > best:
                best = v
            run += total(l, r)
        return best

    # O(log^2 n) -- max sum of a prefix of the path a -> b (a stretch starting at a); -inf when a == b (no edges)
    def edgePathMaxPrefixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMaxPrefixSum", a, b)
        return self._maxPrefixSum(a, b)

    # O(log^2 n) -- max sum of a suffix of the path a -> b (a stretch ending at b); -inf when a == b (no edges)
    def edgePathMaxSuffixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMaxSuffixSum", a, b)
        return self._maxPrefixSum(b, a)

    def _minPrefixSum(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        starting, ending, total = self.seg.minPrefixSum, self.seg.minSuffixSum, self.seg.rangeSum
        run, best = 0, float("inf")  # the sum of the pieces already walked; the best prefix so far
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                v = run + ending(l, r)
                if v < best:
                    best = v
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            v = run + ending(l, r)
            if v < best:
                best = v
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            v = run + starting(l, r)
            if v < best:
                best = v
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            v = run + starting(l, r)
            if v < best:
                best = v
            run += total(l, r)
        return best

    # O(log^2 n) -- min sum of a prefix of the path a -> b (a stretch starting at a); inf when a == b (no edges)
    def edgePathMinPrefixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMinPrefixSum", a, b)
        return self._minPrefixSum(a, b)

    # O(log^2 n) -- min sum of a suffix of the path a -> b (a stretch ending at b); inf when a == b (no edges)
    def edgePathMinSuffixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMinSuffixSum", a, b)
        return self._minPrefixSum(b, a)

    def _firstPrefixSumGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.seg
        first, last, total = seg.leftmostPrefixSumGteX, seg.rightmostSuffixSumGteX, seg.rangeSum
        run = 0  # the sum of the pieces already walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x - run)
                if i != -1:
                    return order[i]
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        return -1

    # O(log^2 n) -- first edge walking a -> b where the sum from a to it is >= x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathFirstPrefixSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstPrefixSumGteX", a, b)
        return self._firstPrefixSumGteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is >= x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathLastSuffixSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumGteX", a, b)
        return self._firstPrefixSumGteX(b, a, x)

    def _firstPrefixSumGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.seg
        first, last, total = seg.leftmostPrefixSumGtX, seg.rightmostSuffixSumGtX, seg.rangeSum
        run = 0  # the sum of the pieces already walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x - run)
                if i != -1:
                    return order[i]
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        return -1

    # O(log^2 n) -- first edge walking a -> b where the sum from a to it is > x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathFirstPrefixSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstPrefixSumGtX", a, b)
        return self._firstPrefixSumGtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is > x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathLastSuffixSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumGtX", a, b)
        return self._firstPrefixSumGtX(b, a, x)

    def _firstPrefixSumLteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.seg
        first, last, total = seg.leftmostPrefixSumLteX, seg.rightmostSuffixSumLteX, seg.rangeSum
        run = 0  # the sum of the pieces already walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x - run)
                if i != -1:
                    return order[i]
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        return -1

    # O(log^2 n) -- first edge walking a -> b where the sum from a to it is <= x, as its lower end (-1 if none)
    def edgePathFirstPrefixSumLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstPrefixSumLteX", a, b)
        return self._firstPrefixSumLteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is <= x, as its lower end (-1 if none)
    def edgePathLastSuffixSumLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumLteX", a, b)
        return self._firstPrefixSumLteX(b, a, x)

    def _firstPrefixSumLtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.seg
        first, last, total = seg.leftmostPrefixSumLtX, seg.rightmostSuffixSumLtX, seg.rangeSum
        run = 0  # the sum of the pieces already walked
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x - run)
                if i != -1:
                    return order[i]
                run += total(l, r)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        return -1

    # O(log^2 n) -- first edge walking a -> b where the sum from a to it is < x, as its lower end (-1 if none)
    def edgePathFirstPrefixSumLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstPrefixSumLtX", a, b)
        return self._firstPrefixSumLtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is < x, as its lower end (-1 if none)
    def edgePathLastSuffixSumLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumLtX", a, b)
        return self._firstPrefixSumLtX(b, a, x)

    # O(log n * log U) -- weight = w for every edge in node's subtree
    def edgeSubtreeAssign(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAssign", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.seg.rangeAssign(l, r, w)

    # O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSum", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.rangeSum(l, r)

    # O(log n + log U) -- gcd of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeGcd(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeGcd", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.rangeGcd(l, r)

    # O(log n) -- xor of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeXOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeXOR", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.rangeXorQuery(l, r)

    # O(log n) -- AND of the edge weights in node's subtree; -1 (every bit set) when node is a leaf (no edges)
    def edgeSubtreeAND(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAND", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return -1
        return self.seg.rangeAndQuery(l, r)

    # O(log n) -- OR of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeOR", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.rangeOrQuery(l, r)

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        head, par, dep = self.head, self.par, self.dep
        while head[a] != head[b]:
            if dep[head[a]] > dep[head[b]]:
                a = par[head[a]]
            else:
                b = par[head[b]]
        return a if dep[a] < dep[b] else b

    # the node k steps above node (k <= its depth): a whole chain at a time
    def _kth(self, node, k):
        head, pos, par = self.head, self.pos, self.par
        while True:
            h = head[node]
            d = pos[node] - pos[h]
            if k <= d:
                return self.order[pos[node] - k]
            k -= d + 1
            node = par[h]

    def _dist(self, a, b):
        dep = self.dep
        return dep[a] + dep[b] - 2 * dep[self._lca(a, b)]

    # of the three pairwise lcas two are equal and the third, the deeper one, is the median
    def _median(self, a, b, c):
        dep = self.dep
        x, y, z = self._lca(a, b), self._lca(a, c), self._lca(b, c)
        if dep[y] > dep[x]:
            x = y
        return z if dep[z] > dep[x] else x

    def _isAncestor(self, a, b):
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    def _onPath(self, a, b, node):
        return self._isAncestor(self._lca(a, b), node) and (self._isAncestor(node, a) or self._isAncestor(node, b))

    # the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    def _next(self, a, b):
        if self._isAncestor(a, b):
            return self._kth(b, self.dep[b] - self.dep[a] - 1)
        return self.par[a]

    # O(log n) -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # O(log n) -- number of edges on the path a..b
    def unweightedDist(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("unweightedDist", a, b)
        return self.dep[a] + self.dep[b] - 2 * self.dep[self._lca(a, b)]

    # O(1) -- edges from the root to node (the root is depth 0)
    def depth(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("depth", node)
        return self.dep[node]

    # O(1) -- node's parent (-1 for the root)
    def parent(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("parent", node)
        return self.par[node]

    # O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    def kthAncestor(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("kthAncestor", node)
        if k < 0:
            raise IndexError(f"kthAncestor: needs k >= 0, got {k}")
        return self._kth(node, k) if k <= self.dep[node] else -1

    # O(1) -- is a an ancestor of b? (True when a == b)
    def isAncestor(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("isAncestor", a, b)
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    # O(1) -- number of nodes in node's subtree (node included)
    def subtreeSize(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("subtreeSize", node)
        return self.sz[node]

    # O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    def countAtDepthInSubtree(self, node, d):
        if not self.lo <= node <= self.hi:
            self._bad("countAtDepthInSubtree", node)
        if d < 0 or d + 1 >= len(self.depthStart):
            return 0
        s, e = self.depthStart[d], self.depthStart[d + 1]
        l = self.pos[node]
        return bisect_left(self.depthPos, l + self.sz[node], s, e) - bisect_left(self.depthPos, l, s, e)

    # O(log n) -- lca of a and b if the tree were rooted at r instead
    def lcaRootedAt(self, r, a, b):
        if not (self.lo <= r <= self.hi and self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lcaRootedAt", r, a, b)
        return self._median(a, b, r)

    # O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    def parentRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("parentRootedAt", r, node)
        return -1 if node == r else self._next(node, r)

    # O(log n) -- size of node's subtree if the tree were rooted at r
    def subtreeSizeRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("subtreeSizeRootedAt", r, node)
        if node == r:
            return self.n
        if self._isAncestor(node, r):  # r hangs below node: everything but the child holding r
            return self.n - self.sz[self._kth(r, self.dep[r] - self.dep[node] - 1)]
        return self.sz[node]

    # O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    # k >= 0
    def kthNodeOnPath(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("kthNodeOnPath", a, b)
        if k < 0:
            raise IndexError(f"kthNodeOnPath: needs k >= 0, got {k}")
        dep = self.dep
        c = self._lca(a, b)
        up = dep[a] - dep[c]
        total = up + dep[b] - dep[c]
        if k > total:
            return -1
        return self._kth(a, k) if k <= up else self._kth(b, total - k)

    # O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    def nextNodeOnPath(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nextNodeOnPath", a, b)
        return -1 if a == b else self._next(a, b)

    # O(log n) -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # O(log n) -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # O(log n) -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    def pathNodes(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("pathNodes", a, b)
        par = self.par
        c = self._lca(a, b)
        out = []
        while a != c:
            out.append(a)
            a = par[a]
        out.append(c)
        tail = []
        while b != c:
            tail.append(b)
            b = par[b]
        tail.reverse()
        return out + tail
