# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-seg-tree-sum-min-max-hash-pre-suf-best-or/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/seg-tree-sum-min-max-hash-pre-suf-best-or/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgeNearestAncestorGtX edgeNearestAncestorGteX edgeNearestAncestorLtX edgeNearestAncestorLteX edgePathFirstGtX edgePathFirstGteX edgePathFirstLtX edgePathFirstLteX edgePathFirstPrefixSumGtX edgePathFirstPrefixSumGteX edgePathHash edgePathHashReversed edgePathIsPalindrome edgePathLastGtX edgePathLastGteX edgePathLastLtX edgePathLastLteX edgePathLastSuffixSumGtX edgePathLastSuffixSumGteX edgePathMax edgePathMaxPrefixSum edgePathMaxSubarraySum edgePathMaxSuffixSum edgePathMin edgePathOR edgePathSum edgePathsEqual edgeSubtreeMax edgeSubtreeMin edgeSubtreeOR edgeSubtreeSum isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodeNearestAncestorGtX nodeNearestAncestorGteX nodeNearestAncestorLtX nodeNearestAncestorLteX nodePathFirstGtX nodePathFirstGteX nodePathFirstLtX nodePathFirstLteX nodePathFirstPrefixSumGtX nodePathFirstPrefixSumGteX nodePathHash nodePathHashReversed nodePathIsPalindrome nodePathLastGtX nodePathLastGteX nodePathLastLtX nodePathLastLteX nodePathLastSuffixSumGtX nodePathLastSuffixSumGteX nodePathMax nodePathMaxPrefixSum nodePathMaxSubarraySum nodePathMaxSuffixSum nodePathMin nodePathOR nodePathSum nodePathsEqual nodeSubtreeMax nodeSubtreeMin nodeSubtreeOR nodeSubtreeSum parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)
#   edgeAssign: log(N)
#   edgeChmax: log(N)
#   edgeChmin: log(N)
#   edgeGet: log(N)
#   edgeNearestAncestorGtX: log^2(N)
#   edgeNearestAncestorGteX: log^2(N)
#   edgeNearestAncestorLtX: log^2(N)
#   edgeNearestAncestorLteX: log^2(N)
#   edgePathFirstGtX: log^2(N)
#   edgePathFirstGteX: log^2(N)
#   edgePathFirstLtX: log^2(N)
#   edgePathFirstLteX: log^2(N)
#   edgePathFirstPrefixSumGtX: log^2(N)
#   edgePathFirstPrefixSumGteX: log^2(N)
#   edgePathHash: log^2(N)
#   edgePathHashReversed: log^2(N)
#   edgePathIsPalindrome: log^2(N)
#   edgePathLastGtX: log^2(N)
#   edgePathLastGteX: log^2(N)
#   edgePathLastLtX: log^2(N)
#   edgePathLastLteX: log^2(N)
#   edgePathLastSuffixSumGtX: log^2(N)
#   edgePathLastSuffixSumGteX: log^2(N)
#   edgePathMax: log^2(N)
#   edgePathMaxPrefixSum: log^2(N)
#   edgePathMaxSubarraySum: log^2(N)
#   edgePathMaxSuffixSum: log^2(N)
#   edgePathMin: log^2(N)
#   edgePathOR: log^2(N)
#   edgePathSum: log^2(N)
#   edgePathsEqual: log^2(N)
#   edgeSubtreeMax: log(N)
#   edgeSubtreeMin: log(N)
#   edgeSubtreeOR: log(N)
#   edgeSubtreeSum: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAdd: log(N)
#   nodeAssign: log(N)
#   nodeChmax: log(N)
#   nodeChmin: log(N)
#   nodeGet: log(N)
#   nodeNearestAncestorGtX: log^2(N)
#   nodeNearestAncestorGteX: log^2(N)
#   nodeNearestAncestorLtX: log^2(N)
#   nodeNearestAncestorLteX: log^2(N)
#   nodePathFirstGtX: log^2(N)
#   nodePathFirstGteX: log^2(N)
#   nodePathFirstLtX: log^2(N)
#   nodePathFirstLteX: log^2(N)
#   nodePathFirstPrefixSumGtX: log^2(N)
#   nodePathFirstPrefixSumGteX: log^2(N)
#   nodePathHash: log^2(N)
#   nodePathHashReversed: log^2(N)
#   nodePathIsPalindrome: log^2(N)
#   nodePathLastGtX: log^2(N)
#   nodePathLastGteX: log^2(N)
#   nodePathLastLtX: log^2(N)
#   nodePathLastLteX: log^2(N)
#   nodePathLastSuffixSumGtX: log^2(N)
#   nodePathLastSuffixSumGteX: log^2(N)
#   nodePathMax: log^2(N)
#   nodePathMaxPrefixSum: log^2(N)
#   nodePathMaxSubarraySum: log^2(N)
#   nodePathMaxSuffixSum: log^2(N)
#   nodePathMin: log^2(N)
#   nodePathOR: log^2(N)
#   nodePathSum: log^2(N)
#   nodePathsEqual: log^2(N)
#   nodeSubtreeMax: log(N)
#   nodeSubtreeMin: log(N)
#   nodeSubtreeOR: log(N)
#   nodeSubtreeSum: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: sm[4*N] mn[4*N] mx[4*N] fh[4*N] bh[4*N] pre[4*N] suf[4*N] best[4*N] orr[4*N]
#   tags: none
#   other: PW[2*log(N)] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

# Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
# its sum, its min, its max, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its
# best subarray sum, its OR over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when
# nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its
# level); an update rewrites a leaf, then its ancestors.
import random


_HP = (1 << 61) - 1  # range hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


INF, NEG = float("inf"), float("-inf")


class SegTree:
    __slots__ = ('n', 'h', 'sm', 'mn', 'mx', 'fh', 'bh', 'pre', 'suf', 'best', 'orr', 'PW')


    # O(N) -- arr: the initial array (non-empty)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.sm = [0] * n + list(arr)
        self.mn = [0] * n + list(arr)
        self.mx = [0] * n + list(arr)
        self.fh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.bh = [0] * n + [(v + _HO) % _HP for v in arr]
        self.pre = [0] * n + list(arr)
        self.suf = [0] * n + list(arr)
        self.best = [0] * n + list(arr)
        self.orr = [0] * n + list(arr)
        pw = self.PW = [_HB]  # PW[s] = B^(2^s): the hash power of a level-s node
        while len(pw) <= self.h:
            pw.append(pw[-1] * pw[-1] % _HP)
        for x in range(n - 1, 0, -1):
            s, y = 0, x
            while y < n:  # (x's level: down its left edge to the leaves)
                y <<= 1
                s += 1
            self._pull(x, s)

    # O(N) -- the whole array
    def getAll(self):
        return self.sm[self.n:]

    # O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs 0 <= l <= r < n, else IndexError
    def isPalindrome(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"isPalindrome: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        fh, bh, pw, P, f, b, p = self.fh, self.bh, self.PW, _HP, 0, 0, 1
        for t, s in self._nodes(l, r):
            f = (f * pw[s] + fh[t]) % P
            b = (bh[t] * p + b) % P
            p = p * pw[s] % P
        return f == b

    # O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def leftmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in self._nodes(l, r):
            if F[t] > x:  # the first covering node with a passing value: walk down it
                while t < n:
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
                    t = 2 * t if F[2 * t] <= x else 2 * t + 1
                return t - n
        return -1

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
                    if acc + P[2 * t] >= x:
                        t = 2 * t
                    else:
                        acc += sm[2 * t]
                        t = 2 * t + 1
                return t - n
            acc += sm[t]
        return -1

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

    # O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    # 0 <= l <= r < n, else IndexError
    def rangeHash(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeHash: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        fh, pw, P, res = self.fh, self.PW, _HP, 0
        for t, s in self._nodes(l, r):
            res = (res * pw[s] + fh[t]) % P
        return res

    # O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs 0 <= l <= r < n, else
    # IndexError
    def rangeHashReversed(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeHashReversed: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        bh, pw, P, res, p = self.bh, self.PW, _HP, 0, 1
        for t, s in self._nodes(l, r):  # (each node read backwards goes in front of what came before it)
            res = (bh[t] * p + res) % P
            p = p * pw[s] % P
        return res

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
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

    # O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    # 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, else IndexError
    def rangesEqual(self, l1, r1, l2, r2):
        if not (0 <= l1 <= r1 < self.n and 0 <= l2 <= r2 < self.n):
            raise IndexError(f"rangesEqual: needs 0 <= l1 <= r1 < n and 0 <= l2 <= r2 < n, got "
                             f"l1 = {l1}, r1 = {r1}, l2 = {l2}, r2 = {r2}, n = {self.n}")
        return r1 - l1 == r2 - l2 and self.rangeHash(l1, r1) == self.rangeHash(l2, r2)

    # O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    # else IndexError
    def rightmostGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n, F = self.n, self.mx
        for t, s in reversed(self._nodes(l, r)):
            if F[t] > x:  # the last covering node with a passing value: walk down it
                while t < n:
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
                    t = 2 * t + 1 if F[2 * t + 1] <= x else 2 * t
                return t - n
        return -1

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
                    if acc + P[2 * t + 1] >= x:
                        t = 2 * t + 1
                    else:
                        acc += sm[2 * t + 1]
                        t = 2 * t
                return t - n
            acc += sm[t]
        return -1

    # O(log^2(N)) -- (l, r) of the longest odd palindrome a[l..r] centred on a[i] (at least (i, i)): a binary search on
    # its radius, log N calls of isPalindrome; needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtI(self, i):
        n = self.n
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtI: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo, i + lo

    # O(log^2(N)) -- (l, r) of the longest even palindrome a[l..r] centred between a[i] and a[i+1]; (i + 1, i), the
    # empty
    # range, when there is none (so also for i = n - 1): a binary search on its radius, log N calls of isPalindrome;
    # needs 0 <= i < n, else raises IndexError
    def longestPalCenteredAtIPlusOne(self, i):
        n = self.n
        if not 0 <= i < n:
            raise IndexError(f"longestPalCenteredAtIPlusOne: needs 0 <= i < n, got i = {i}, n = {n}")
        lo, hi = 0, min(i + 1, n - 1 - i)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self.isPalindrome(i - mid + 1, i + mid):
                lo = mid
            else:
                hi = mid - 1
        return i - lo + 1, i + lo

    # O(log(N)) -- hash of the whole array a[0..n-1]: the same base and mod as rangeHash (shared by every structure
    # this run, so it compares with another one's hashes); needs n >= 1, else raises IndexError
    def hashAll(self):
        if self.n < 1:
            raise IndexError("hashAll: needs n >= 1")
        return self.rangeHash(0, self.n - 1)

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)

    # O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)

    # O(log(N)) -- hash of the whole array reversed, a[n-1], ..., a[0] (rangeHashReversed(0, n - 1)); it uses the same
    # base and mod as rangeHash, so it equals rangeHash of any range holding those values in that order (and any
    # structure's hashes this run); needs n >= 1, else raises IndexError
    def hashAllReversed(self):
        if self.n < 1:
            raise IndexError("hashAllReversed: needs n >= 1")
        return self.rangeHashReversed(0, self.n - 1)

    # ---- internals ----

    def _setLeaf(self, p, v):  # leaf p holds v alone
        self.sm[p] = v
        self.mn[p] = v
        self.mx[p] = v
        self.fh[p] = (v + _HO) % _HP
        self.bh[p] = (v + _HO) % _HP
        self.pre[p] = v
        self.suf[p] = v
        self.best[p] = v
        self.orr[p] = v

    def _leaf(self, p):  # the value at leaf p
        return self.sm[p]

    def _pull(self, x, s):  # recompute node x (level s) from its children
        a, b = 2 * x, 2 * x + 1
        sm = self.sm
        self.pre[x] = max(self.pre[a], sm[a] + self.pre[b])
        self.suf[x] = max(self.suf[b], sm[b] + self.suf[a])
        self.best[x] = max(self.best[a], self.best[b], self.suf[a] + self.pre[b])
        sm[x] = sm[a] + sm[b]
        u, w = self.mn[a], self.mn[b]
        self.mn[x] = u if u < w else w
        u, w = self.mx[a], self.mx[b]
        self.mx[x] = u if u > w else w
        k = self.PW[s - 1]
        self.fh[x] = (self.fh[a] * k + self.fh[b]) % _HP
        self.bh[x] = (self.bh[b] * k + self.bh[a]) % _HP
        self.orr[x] = self.orr[a] | self.orr[b]

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


from bisect import bisect_left


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
# nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
# edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
# (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
# returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (SegTree) sit
# over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower end's
# position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain it
# crosses.
class Tree:
    # O(n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
    def __init__(self, edges, root, vals):
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
        if len(vals) != hi + 1:
            raise ValueError(f"Tree: vals[node] is node's value, so nodes {lo}..{hi} need len(vals) = {hi + 1}"
                             f"{' (vals[0] is ignored)' if lo else ''}, got {len(vals)}")
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        arr = [edges[0][2] if edges else 0] * n  # (position 0 is the root's: it holds no edge, never read)
        for e in edges:
            a, b = e[0], e[1]
            arr[pos[a] if par[a] == b else pos[b]] = e[2]
        self.nodeSeg = SegTree([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = SegTree(arr)  # each edge's weight, at its lower end's position

    # O(log n) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(log n) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.nodeSeg.pointAssign(self.pos[node], x)

    # O(log n) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.nodeSeg.pointAdd(self.pos[node], x)

    # O(log n) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.nodeSeg.pointChmax(self.pos[node], x)

    # O(log n) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.nodeSeg.pointChmin(self.pos[node], x)

    # O(log^2 n) -- sum of the node values on the path a..b
    def nodePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeSum
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r)
        return res

    # O(log^2 n) -- min node value on the path a..b
    def nodePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeMin
        res = float("inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v < res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r)
        if v < res:
            res = v
        return res

    # O(log^2 n) -- max node value on the path a..b
    def nodePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMax", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeMax
        res = float("-inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v > res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        v = query(l, r)
        if v > res:
            res = v
        return res

    # O(log^2 n) -- OR of the node values on the path a..b
    def nodePathOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathOR", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeOrQuery
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res |= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res |= query(l, r)
        return res

    # O(log^2 n) -- max sum of a non-empty stretch of the path a..b
    def nodePathMaxSubarraySum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMaxSubarraySum", a, b)
        head, par, dep, pos, seg = self.head, self.par, self.dep, self.pos, self.nodeSeg
        total, starting, ending, inside = seg.rangeSum, seg.maxPrefixSum, seg.maxSuffixSum, seg.maxSubarraySum
        best = tail = float("-inf")  # the best stretch so far; the best one ending at the last node walked
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
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            s, inner = total(l, r), inside(l, r)
            if inner > best:
                best = inner
            v = tail + ending(l, r)
            if v > best:
                best = v
            v = starting(l, r)
            tail = v if v > tail + s else tail + s
        else:
            l, r = pos[a], pos[b]
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

    # the hash of the node values read walking a -> b
    def _nodeHash(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        forward, back = self.nodeSeg.rangeHash, self.nodeSeg.rangeHashReversed
        res = 0
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                res = (res * pow(_HB, r - l + 1, _HP) + back(l, r)) % _HP
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            res = (res * pow(_HB, r - l + 1, _HP) + back(l, r)) % _HP
        else:
            l, r = pos[a], pos[b]
            res = (res * pow(_HB, r - l + 1, _HP) + forward(l, r)) % _HP
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            res = (res * pow(_HB, r - l + 1, _HP) + forward(l, r)) % _HP
        return res

    # O(log^2 n) -- hash of the node values read a -> b: equal sequences hash equal, and it equals the range structure's
    # rangeHash of the same values
    def nodePathHash(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathHash", a, b)
        return self._nodeHash(a, b)

    # O(log^2 n) -- hash of the node values read b -> a (equal to nodePathHash(b, a))
    def nodePathHashReversed(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathHashReversed", a, b)
        return self._nodeHash(b, a)

    # O(log^2 n) -- do the node values read the same a -> b and b -> a?
    def nodePathIsPalindrome(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathIsPalindrome", a, b)
        return self._nodeHash(a, b) == self._nodeHash(b, a)

    # O(log^2 n) -- do the node values read a -> b equal those read c -> d?
    def nodePathsEqual(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("nodePathsEqual", a, b, c, d)
        return self._dist(a, b) == self._dist(c, d) and self._nodeHash(a, b) == self._nodeHash(c, d)

    def _nodeMaxPrefixSum(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        starting, ending, total = self.nodeSeg.maxPrefixSum, self.nodeSeg.maxSuffixSum, self.nodeSeg.rangeSum
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
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            v = run + ending(l, r)
            if v > best:
                best = v
            run += total(l, r)
        else:
            l, r = pos[a], pos[b]
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

    # O(log^2 n) -- max sum of a prefix of the path a -> b (a stretch starting at a)
    def nodePathMaxPrefixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMaxPrefixSum", a, b)
        return self._nodeMaxPrefixSum(a, b)

    # O(log^2 n) -- max sum of a suffix of the path a -> b (a stretch ending at b)
    def nodePathMaxSuffixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMaxSuffixSum", a, b)
        return self._nodeMaxPrefixSum(b, a)

    # O(log^2 n) -- nearest ancestor of node (node included) with val >= x (-1 if none)
    def nodeNearestAncestorGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorGteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostGteX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostGteX, self.nodeSeg.rightmostGteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val >= x (-1 if none)
    def nodePathFirstGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstGteX", a, b)
        return self._nodeFirstGteX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val >= x (-1 if none)
    def nodePathLastGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastGteX", a, b)
        return self._nodeFirstGteX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val > x (-1 if none)
    def nodeNearestAncestorGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorGtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostGtX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostGtX, self.nodeSeg.rightmostGtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val > x (-1 if none)
    def nodePathFirstGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstGtX", a, b)
        return self._nodeFirstGtX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val > x (-1 if none)
    def nodePathLastGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastGtX", a, b)
        return self._nodeFirstGtX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val <= x (-1 if none)
    def nodeNearestAncestorLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorLteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostLteX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstLteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostLteX, self.nodeSeg.rightmostLteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val <= x (-1 if none)
    def nodePathFirstLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstLteX", a, b)
        return self._nodeFirstLteX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val <= x (-1 if none)
    def nodePathLastLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastLteX", a, b)
        return self._nodeFirstLteX(b, a, x)

    # O(log^2 n) -- nearest ancestor of node (node included) with val < x (-1 if none)
    def nodeNearestAncestorLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorLtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostLtX
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstLtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostLtX, self.nodeSeg.rightmostLtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val < x (-1 if none)
    def nodePathFirstLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstLtX", a, b)
        return self._nodeFirstLtX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val < x (-1 if none)
    def nodePathLastLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastLtX", a, b)
        return self._nodeFirstLtX(b, a, x)

    def _nodeFirstPrefixSumGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.nodeSeg
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
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        else:
            l, r = pos[a], pos[b]
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

    # O(log^2 n) -- first node walking a -> b where the sum from a to it is >= x (-1 if none) (needs every val >= 0)
    def nodePathFirstPrefixSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstPrefixSumGteX", a, b)
        return self._nodeFirstPrefixSumGteX(a, b, x)

    # O(log^2 n) -- last node walking a -> b where the sum from it to b is >= x (-1 if none) (needs every val >= 0)
    def nodePathLastSuffixSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastSuffixSumGteX", a, b)
        return self._nodeFirstPrefixSumGteX(b, a, x)

    def _nodeFirstPrefixSumGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.nodeSeg
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
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x - run)
            if i != -1:
                return order[i]
            run += total(l, r)
        else:
            l, r = pos[a], pos[b]
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

    # O(log^2 n) -- first node walking a -> b where the sum from a to it is > x (-1 if none) (needs every val >= 0)
    def nodePathFirstPrefixSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstPrefixSumGtX", a, b)
        return self._nodeFirstPrefixSumGtX(a, b, x)

    # O(log^2 n) -- last node walking a -> b where the sum from it to b is > x (-1 if none) (needs every val >= 0)
    def nodePathLastSuffixSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastSuffixSumGtX", a, b)
        return self._nodeFirstPrefixSumGtX(b, a, x)

    # O(log n) -- sum of the node values in node's subtree
    def nodeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSum", node)
        l = self.pos[node]
        return self.nodeSeg.rangeSum(l, l + self.sz[node] - 1)

    # O(log n) -- min node value in node's subtree
    def nodeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMin", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMin(l, l + self.sz[node] - 1)

    # O(log n) -- max node value in node's subtree
    def nodeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMax", node)
        l = self.pos[node]
        return self.nodeSeg.rangeMax(l, l + self.sz[node] - 1)

    # O(log n) -- OR of the node values in node's subtree
    def nodeSubtreeOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeOR", node)
        l = self.pos[node]
        return self.nodeSeg.rangeOrQuery(l, l + self.sz[node] - 1)

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
        return self.edgeSeg.pointGet(self._edge("edgeGet", a, b))

    # O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.edgeSeg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        self.edgeSeg.pointAdd(self._edge("edgeAdd", a, b), w)

    # O(log n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        self.edgeSeg.pointChmax(self._edge("edgeChmax", a, b), w)

    # O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        self.edgeSeg.pointChmin(self._edge("edgeChmin", a, b), w)

    # O(log^2 n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeSum
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

    # O(log^2 n) -- min edge weight on the path a..b; inf when a == b (no edges)
    def edgePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeMin
        res = float("inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v < res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r)
            if v < res:
                res = v
        return res

    # O(log^2 n) -- max edge weight on the path a..b; -inf when a == b (no edges)
    def edgePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMax", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeMax
        res = float("-inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a])
            if v > res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r)
            if v > res:
                res = v
        return res

    # O(log^2 n) -- OR of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathOR", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeOrQuery
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
        head, par, dep, pos, seg = self.head, self.par, self.dep, self.pos, self.edgeSeg
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

    # the hash of the edge weights read walking a -> b
    def _edgeHash(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        forward, back = self.edgeSeg.rangeHash, self.edgeSeg.rangeHashReversed
        res = 0
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                res = (res * pow(_HB, r - l + 1, _HP) + back(l, r)) % _HP
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            res = (res * pow(_HB, r - l + 1, _HP) + back(l, r)) % _HP
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            res = (res * pow(_HB, r - l + 1, _HP) + forward(l, r)) % _HP
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            res = (res * pow(_HB, r - l + 1, _HP) + forward(l, r)) % _HP
        return res

    # O(log^2 n) -- hash of the edge weights read a -> b: equal sequences hash equal, and it equals the range
    # structure's rangeHash of the same values; 0 when a == b (no edges)
    def edgePathHash(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathHash", a, b)
        return self._edgeHash(a, b)

    # O(log^2 n) -- hash of the edge weights read b -> a (equal to edgePathHash(b, a)); 0 when a == b (no edges)
    def edgePathHashReversed(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathHashReversed", a, b)
        return self._edgeHash(b, a)

    # O(log^2 n) -- do the edge weights read the same a -> b and b -> a? (True when a == b: no edges)
    def edgePathIsPalindrome(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathIsPalindrome", a, b)
        return self._edgeHash(a, b) == self._edgeHash(b, a)

    # O(log^2 n) -- do the edge weights read a -> b equal those read c -> d? (two paths with no edges are equal)
    def edgePathsEqual(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("edgePathsEqual", a, b, c, d)
        return self._dist(a, b) == self._dist(c, d) and self._edgeHash(a, b) == self._edgeHash(c, d)

    def _edgeMaxPrefixSum(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        starting, ending, total = self.edgeSeg.maxPrefixSum, self.edgeSeg.maxSuffixSum, self.edgeSeg.rangeSum
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
        return self._edgeMaxPrefixSum(a, b)

    # O(log^2 n) -- max sum of a suffix of the path a -> b (a stretch ending at b); -inf when a == b (no edges)
    def edgePathMaxSuffixSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMaxSuffixSum", a, b)
        return self._edgeMaxPrefixSum(b, a)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight >= x, as its lower end (-1 if none)
    def edgeNearestAncestorGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorGteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostGteX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostGteX, self.edgeSeg.rightmostGteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight >= x, as its lower end (-1 if none)
    def edgePathFirstGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstGteX", a, b)
        return self._edgeFirstGteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight >= x, as its lower end (-1 if none)
    def edgePathLastGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastGteX", a, b)
        return self._edgeFirstGteX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight > x, as its lower end (-1 if none)
    def edgeNearestAncestorGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorGtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostGtX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostGtX, self.edgeSeg.rightmostGtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight > x, as its lower end (-1 if none)
    def edgePathFirstGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstGtX", a, b)
        return self._edgeFirstGtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight > x, as its lower end (-1 if none)
    def edgePathLastGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastGtX", a, b)
        return self._edgeFirstGtX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight <= x, as its lower end (-1 if none)
    def edgeNearestAncestorLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorLteX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostLteX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstLteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostLteX, self.edgeSeg.rightmostLteX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight <= x, as its lower end (-1 if none)
    def edgePathFirstLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstLteX", a, b)
        return self._edgeFirstLteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight <= x, as its lower end (-1 if none)
    def edgePathLastLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastLteX", a, b)
        return self._edgeFirstLteX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight < x, as its lower end (-1 if none)
    def edgeNearestAncestorLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorLtX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostLtX
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstLtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostLtX, self.edgeSeg.rightmostLtX
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight < x, as its lower end (-1 if none)
    def edgePathFirstLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstLtX", a, b)
        return self._edgeFirstLtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight < x, as its lower end (-1 if none)
    def edgePathLastLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastLtX", a, b)
        return self._edgeFirstLtX(b, a, x)

    def _edgeFirstPrefixSumGteX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.edgeSeg
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
        return self._edgeFirstPrefixSumGteX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is >= x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathLastSuffixSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumGteX", a, b)
        return self._edgeFirstPrefixSumGteX(b, a, x)

    def _edgeFirstPrefixSumGtX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        seg = self.edgeSeg
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
        return self._edgeFirstPrefixSumGtX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b where the sum from it to b is > x, as its lower end (-1 if none) (needs
    # every weight >= 0)
    def edgePathLastSuffixSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastSuffixSumGtX", a, b)
        return self._edgeFirstPrefixSumGtX(b, a, x)

    # O(log n) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSum", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.rangeSum(l, r)

    # O(log n) -- min edge weight in node's subtree; inf when node is a leaf (no edges)
    def edgeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMin", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("inf")
        return self.edgeSeg.rangeMin(l, r)

    # O(log n) -- max edge weight in node's subtree; -inf when node is a leaf (no edges)
    def edgeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMax", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("-inf")
        return self.edgeSeg.rangeMax(l, r)

    # O(log n) -- OR of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeOR", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.rangeOrQuery(l, r)

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
