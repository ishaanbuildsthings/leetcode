# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/edge-bit-of-tries-xor/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-tries-xor/template.py
# @operations: countAtDepthInSubtree depth edgeAssign edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMaxXorAgainstX edgePathMin edgePathMinXorAgainstX edgePathSmallestGtX edgePathSmallestGteX edgeSubtreeCountGtX edgeSubtreeCountGteX edgeSubtreeCountInValRange edgeSubtreeCountLtX edgeSubtreeCountLteX edgeSubtreeCountOccurrences edgeSubtreeKthSmallest edgeSubtreeLargestLtX edgeSubtreeLargestLteX edgeSubtreeMax edgeSubtreeMaxXorAgainstX edgeSubtreeMin edgeSubtreeMinXorAgainstX edgeSubtreeSmallestGtX edgeSubtreeSmallestGteX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: bit-of-tries
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAssign: log(N)*log(U)
#   edgeGet: 1
#   edgePathCountGtX: log^2(N)*log(U)
#   edgePathCountGteX: log^2(N)*log(U)
#   edgePathCountInValRange: log^2(N)*log(U)
#   edgePathCountLtX: log^2(N)*log(U)
#   edgePathCountLteX: log^2(N)*log(U)
#   edgePathCountOccurrences: log^2(N)*log(U)
#   edgePathLargestLtX: log^2(N)*log(U)
#   edgePathLargestLteX: log^2(N)*log(U)
#   edgePathMax: log^2(N)*log(U)
#   edgePathMaxXorAgainstX: log^2(N)*log(U)
#   edgePathMin: log^2(N)*log(U)
#   edgePathMinXorAgainstX: log^2(N)*log(U)
#   edgePathSmallestGtX: log^2(N)*log(U)
#   edgePathSmallestGteX: log^2(N)*log(U)
#   edgeSubtreeCountGtX: log(N)*log(U)
#   edgeSubtreeCountGteX: log(N)*log(U)
#   edgeSubtreeCountInValRange: log(N)*log(U)
#   edgeSubtreeCountLtX: log(N)*log(U)
#   edgeSubtreeCountLteX: log(N)*log(U)
#   edgeSubtreeCountOccurrences: log(N)*log(U)
#   edgeSubtreeKthSmallest: log(N)*log(U)
#   edgeSubtreeLargestLtX: log(N)*log(U)
#   edgeSubtreeLargestLteX: log(N)*log(U)
#   edgeSubtreeMax: log(N)*log(U)
#   edgeSubtreeMaxXorAgainstX: log(N)*log(U)
#   edgeSubtreeMin: log(N)*log(U)
#   edgeSubtreeMinXorAgainstX: log(N)*log(U)
#   edgeSubtreeSmallestGtX: log(N)*log(U)
#   edgeSubtreeSmallestGteX: log(N)*log(U)
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
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: BIT over positions, each BIT node a binary trie of its block's values (U = 2^bits); nodes are never freed, so each point assign adds up to 2 log N log U of them

# a[l..r] as a multiset, asked about v ^ x over its values v, with point assigns. A Fenwick tree (BIT) over positions:
# BIT node j is a binary trie (one level per bit, highest bit first) of the values a[j - lowbit(j) .. j - 1]. The values
# of a[l..r] are the BIT prefix of r + 1 minus the prefix of l, so a query walks those ~2 log N tries down together
# (adding the first prefix's counts, subtracting the second's). Values and every x must lie in [0, 2^bits); thresholds
# (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
# The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.


class BitXorTries:
    __slots__ = ('B', 'top', 'n', 'arr', 'root', 'L', 'R', 'C')

    # O(N logN logU) -- arr: the initial values (a list), each in [0, 2^bits) (bits = 30 holds values up to 1073741823);
    # U = 2^bits
    def __init__(self, arr, bits):
        self.B, self.top = bits, (1 << bits) - 1
        self.n, self.arr = len(arr), list(arr)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = empty
        self.root = [0] * (self.n + 1)  # root[j] = BIT node j's trie (1-indexed)
        for j in range(1, self.n + 1):
            self.root[j] = self._new()
        for i, v in enumerate(self.arr):
            if not 0 <= v <= self.top:
                raise ValueError(f"__init__: needs 0 <= v < 2^bits, got v = {v} at index {i}, bits = {bits}")
            self._add(i, v, 1)

    # O(logN logU) -- a[i] = v (0 <= v < 2^bits); needs 0 <= i < size(), else IndexError (ValueError for v)
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        if not 0 <= v <= self.top:
            raise ValueError(f"pointAssign: needs 0 <= v < 2^bits, got v = {v}, bits = {self.B}")
        if self.arr[i] != v:
            self._add(i, self.arr[i], -1)
            self._add(i, v, 1)
            self.arr[i] = v

    # O(1) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(N) -- the whole array (a copy)
    def getAll(self):
        return list(self.arr)

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN logU) -- largest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def maxXorAgainstX(self, l, r, x):
        P, N = self._span("maxXorAgainstX", l, r)
        return self._extreme(P, N, self.B - 1, x, 1)

    # O(logN logU) -- smallest v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def minXorAgainstX(self, l, r, x):
        P, N = self._span("minXorAgainstX", l, r)
        return self._extreme(P, N, self.B - 1, x, 0)

    # O(logN logU) -- the i-th smallest of v ^ x over the values v in a[l..r], 0-indexed: kthXor(l, r, x, 0) is the
    # smallest (copies count); needs 0 <= l <= r < size() and 0 <= i <= r - l, else IndexError
    def kthXor(self, l, r, x, i):
        P, N = self._span("kthXor", l, r)
        if not 0 <= i <= r - l:
            raise IndexError(f"kthXor: needs 0 <= i <= r - l, got i = {i}, r - l = {r - l}")
        return self._kthX(P, N, i + 1, x)

    # O(logN logU) -- how many values v in a[l..r] have v ^ x < k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorLtK(self, l, r, x, k):
        P, N = self._span("countXorLtK", l, r)
        return self._cntLt(P, N, r - l + 1, k, x)

    # O(logN logU) -- how many values v in a[l..r] have v ^ x <= k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorLteK(self, l, r, x, k):
        P, N = self._span("countXorLteK", l, r)
        return self._cntLt(P, N, r - l + 1, k + 1, x)

    # O(logN logU) -- how many values v in a[l..r] have v ^ x > k (k is a VALUE, not a rank); needs 0 <= l <= r < size()
    def countXorGtK(self, l, r, x, k):
        P, N = self._span("countXorGtK", l, r)
        return r - l + 1 - self._cntLt(P, N, r - l + 1, k + 1, x)

    # O(logN logU) -- how many values v in a[l..r] have v ^ x >= k (k is a VALUE, not a rank); needs
    # 0 <= l <= r < size()
    def countXorGteK(self, l, r, x, k):
        P, N = self._span("countXorGteK", l, r)
        return r - l + 1 - self._cntLt(P, N, r - l + 1, k, x)

    # O(logN logU) -- largest v ^ x < k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLtK(self, l, r, x, k):
        P, N = self._span("largestXorLtK", l, r)
        c = self._cntLt(P, N, r - l + 1, k, x)
        return self._kthX(P, N, c, x) if c else None

    # O(logN logU) -- largest v ^ x <= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def largestXorLteK(self, l, r, x, k):
        P, N = self._span("largestXorLteK", l, r)
        c = self._cntLt(P, N, r - l + 1, k + 1, x)
        return self._kthX(P, N, c, x) if c else None

    # O(logN logU) -- smallest v ^ x > k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGtK(self, l, r, x, k):
        P, N = self._span("smallestXorGtK", l, r)
        c = self._cntLt(P, N, r - l + 1, k + 1, x)
        return self._kthX(P, N, c + 1, x) if c <= r - l else None

    # O(logN logU) -- smallest v ^ x >= k over the values v in a[l..r] (k is a VALUE, not a rank), or None; needs
    # 0 <= l <= r < size()
    def smallestXorGteK(self, l, r, x, k):
        P, N = self._span("smallestXorGteK", l, r)
        c = self._cntLt(P, N, r - l + 1, k, x)
        return self._kthX(P, N, c + 1, x) if c <= r - l else None


    # O(logN logU) -- largest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLtM(self, l, r, x, m):
        return self._bestIn(*self._span("maxXorWithVLtM", l, r), x, 0, m - 1, 1)

    # O(logN logU) -- largest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVLteM(self, l, r, x, m):
        return self._bestIn(*self._span("maxXorWithVLteM", l, r), x, 0, m, 1)

    # O(logN logU) -- largest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGtM(self, l, r, x, m):
        return self._bestIn(*self._span("maxXorWithVGtM", l, r), x, m + 1, self.top, 1)

    # O(logN logU) -- largest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def maxXorWithVGteM(self, l, r, x, m):
        return self._bestIn(*self._span("maxXorWithVGteM", l, r), x, m, self.top, 1)

    # O(logN logU) -- smallest v ^ x over the values v < m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLtM(self, l, r, x, m):
        return self._bestIn(*self._span("minXorWithVLtM", l, r), x, 0, m - 1, 0)

    # O(logN logU) -- smallest v ^ x over the values v <= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVLteM(self, l, r, x, m):
        return self._bestIn(*self._span("minXorWithVLteM", l, r), x, 0, m, 0)

    # O(logN logU) -- smallest v ^ x over the values v > m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGtM(self, l, r, x, m):
        return self._bestIn(*self._span("minXorWithVGtM", l, r), x, m + 1, self.top, 0)

    # O(logN logU) -- smallest v ^ x over the values v >= m in a[l..r], or None; needs 0 <= l <= r < size()
    def minXorWithVGteM(self, l, r, x, m):
        return self._bestIn(*self._span("minXorWithVGteM", l, r), x, m, self.top, 0)

    # O(logN logU) -- largest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs
    # 0 <= l <= r < size()
    def maxXorWithVInValRange(self, l, r, x, lo, hi):
        return self._bestIn(*self._span("maxXorWithVInValRange", l, r), x, lo, hi, 1)

    # O(logN logU) -- smallest v ^ x over the values v in a[l..r] with lo <= v <= hi, or None; needs
    # 0 <= l <= r < size()
    def minXorWithVInValRange(self, l, r, x, lo, hi):
        return self._bestIn(*self._span("minXorWithVInValRange", l, r), x, lo, hi, 0)

    # ---- plain order statistics over a[l..r] (the same walks with x = 0) ----

    # O(logN logU) -- # of values < x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLtX(self, l, r, x):
        self._rangeCheck("countLtX", l, r)
        return self._lt(l, r, x)

    # O(logN logU) -- # of values <= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countLteX(self, l, r, x):
        self._rangeCheck("countLteX", l, r)
        return self._lt(l, r, x + 1)

    # O(logN logU) -- # of values > x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGtX(self, l, r, x):
        self._rangeCheck("countGtX", l, r)
        return r - l + 1 - self._lt(l, r, x + 1)

    # O(logN logU) -- # of values >= x in a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def countGteX(self, l, r, x):
        self._rangeCheck("countGteX", l, r)
        return r - l + 1 - self._lt(l, r, x)

    # O(logN logU) -- # of values v in a[l..r] with lowVal <= v <= highVal (0 if lowVal > highVal); needs 0 <= l <= r <
    # size()
    def countInValRange(self, l, r, lowVal, highVal):
        self._rangeCheck("countInValRange", l, r)
        return self._lt(l, r, highVal + 1) - self._lt(l, r, lowVal) if lowVal <= highVal else 0

    # O(logN logU) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        self._rangeCheck("countOccurrences", l, r)
        return self._lt(l, r, x + 1) - self._lt(l, r, x)

    # O(logN logU) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < size() and 1 <= k <= r - l +
    # 1, else IndexError
    def kthSmallest(self, l, r, k):
        self._rangeCheck("kthSmallest", l, r)
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN logU) -- min of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMin(self, l, r):
        self._rangeCheck("rangeMin", l, r)
        return self._kth(l, r, 1)

    # O(logN logU) -- max of a[l..r]; needs 0 <= l <= r < size(), else IndexError
    def rangeMax(self, l, r):
        self._rangeCheck("rangeMax", l, r)
        return self._kth(l, r, r - l + 1)

    # O(logN logU) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGteX(self, l, r, x):
        self._rangeCheck("smallestGteX", l, r)
        c = self._lt(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN logU) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def smallestGtX(self, l, r, x):
        self._rangeCheck("smallestGtX", l, r)
        c = self._lt(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN logU) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLteX(self, l, r, x):
        self._rangeCheck("largestLteX", l, r)
        c = self._lt(l, r, x + 1)
        return self._kth(l, r, c) if c else None

    # O(logN logU) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < size(), else IndexError
    def largestLtX(self, l, r, x):
        self._rangeCheck("largestLtX", l, r)
        c = self._lt(l, r, x)
        return self._kth(l, r, c) if c else None

    # O(logN logU) -- min of the whole array; raises IndexError if it is empty
    def minAll(self):
        if not self.size():
            raise IndexError("minAll: the array is empty")
        return self._kth(0, self.size() - 1, 1)

    # O(logN logU) -- max of the whole array; raises IndexError if it is empty
    def maxAll(self):
        if not self.size():
            raise IndexError("maxAll: the array is empty")
        return self._kth(0, self.size() - 1, self.size())

    # ---- internals ----

    def _new(self):
        self.L.append(0), self.R.append(0), self.C.append(0)
        return len(self.C) - 1

    # d copies of v at index i (d = -1 removes one): every BIT node covering i, and the per-bit counts
    def _add(self, i, v, d):
        L, R, C, n = self.L, self.R, self.C, self.n
        j = i + 1
        while j <= n:
            t = self.root[j]
            C[t] += d
            for h in range(self.B - 1, -1, -1):
                if v >> h & 1:
                    u = R[t] or self._new()
                    R[t] = u
                else:
                    u = L[t] or self._new()
                    L[t] = u
                t = u
                C[t] += d
            j += j & -j

    def _rangeCheck(self, name, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"{name}: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.n}")

    # checks 0 <= l <= r < size(); the tries whose counts add up to a[l..r]'s values
    def _span(self, name, l, r):
        self._rangeCheck(name, l, r)
        return self._tries(l, r)

    # the tries whose counts add up to a[l..r]'s values: (prefix r + 1's, prefix l's)
    def _tries(self, l, r):
        root, P, N = self.root, [], []
        j = r + 1
        while j:
            P.append(root[j])
            j &= j - 1
        j = l
        while j:
            N.append(root[j])
            j &= j - 1
        return P, N

    def _lt(self, l, r, k):  # how many values in a[l..r] are < k
        return self._cntLt(*self._tries(l, r), r - l + 1, k, 0)

    def _kth(self, l, r, k):  # the k-th smallest (1-indexed) of a[l..r]
        return self._kthX(*self._tries(l, r), k, 0)

    def _cnt(self, P, N):
        C = self.C
        return sum(C[t] for t in P) - sum(C[t] for t in N)

    def _down(self, P, N, bit):  # the children for v's bit = bit (empty ones dropped)
        K = self.R if bit else self.L
        return [K[t] for t in P if K[t]], [K[t] for t in N if K[t]]

    # how many values v below (P, N) (cnt of them in all) have v ^ x < k
    def _cntLt(self, P, N, cnt, k, x):
        if k <= 0:
            return 0
        if k > self.top:
            return cnt
        res = 0
        for h in range(self.B - 1, -1, -1):
            xb = x >> h & 1
            if k >> h & 1:  # every result with bit h = 0 is < k
                res += self._cnt(*self._down(P, N, xb))
                P, N = self._down(P, N, xb ^ 1)
            else:
                P, N = self._down(P, N, xb)
            if not P:
                break
        return res

    # the k-th smallest (1-indexed) v ^ x over the values below (P, N)
    def _kthX(self, P, N, k, x):
        res = 0
        for h in range(self.B - 1, -1, -1):
            xb = x >> h & 1
            zP, zN = self._down(P, N, xb)
            c = self._cnt(zP, zN)
            if k <= c:
                P, N = zP, zN
            else:
                k -= c
                P, N = self._down(P, N, xb ^ 1)
                res |= 1 << h
        return res

    # bits h..0 of the largest (big = 1) / smallest v ^ x below (P, N), which holds some value
    def _extreme(self, P, N, h, x, big):
        res = 0
        while h >= 0:
            p = (x >> h & 1) ^ big  # the child whose result bit is big
            uP, uN = self._down(P, N, p)
            if self._cnt(uP, uN):
                P, N = uP, uN
                res |= big << h
            else:
                P, N = self._down(P, N, p ^ 1)
                res |= (big ^ 1) << h
            h -= 1
        return res

    # the largest (big = 1) / smallest v ^ x over the values v below (P, N) with lo <= v <= hi, or None. Walks down the
    # bits lo and hi share, then splits: below lo's side only the lower bound matters, below hi's only the upper one
    def _bestIn(self, P, N, x, lo, hi, big):
        lo, hi = max(lo, 0), min(hi, self.top)
        if lo > hi:
            return None
        res, h = 0, self.B - 1
        while h >= 0 and (lo >> h & 1) == (hi >> h & 1):
            bit = lo >> h & 1
            P, N = self._down(P, N, bit)
            if not self._cnt(P, N):
                return None
            res |= (bit ^ (x >> h & 1)) << h
            h -= 1
        if h < 0:
            return res
        xb = x >> h & 1
        c0 = self._oneSide(*self._down(P, N, 0), h - 1, lo, x, big, 1, res | xb << h)
        c1 = self._oneSide(*self._down(P, N, 1), h - 1, hi, x, big, 0, res | (xb ^ 1) << h)
        if c0 is None or c1 is None:
            return c1 if c0 is None else c0
        return max(c0, c1) if big else min(c0, c1)

    # below (P, N): the best v ^ x whose bits h..0 are >= (lower = 1) / <= bound's bits h..0, or None; res holds the
    # result's bits above h. Along the path that matches bound, each step off it (to the side the bound allows) is a
    # free subtree: take it at once if its result bit beats the path's, else remember the deepest one
    def _oneSide(self, P, N, h, bound, x, big, lower, res):
        if not self._cnt(P, N):
            return None
        fallback = None
        while h >= 0:
            xb, bb = x >> h & 1, bound >> h & 1
            if bb != lower:  # a free side exists: v bit = lower
                fP, fN = self._down(P, N, lower)
                if self._cnt(fP, fN):
                    fres = res | (lower ^ xb) << h
                    if lower ^ xb == big:
                        return fres | self._extreme(fP, fN, h - 1, x, big)
                    fallback = (fP, fN, h, fres)
            P, N = self._down(P, N, bb)
            if not self._cnt(P, N):
                break
            res |= (bb ^ xb) << h
            h -= 1
        else:
            return res  # v equal to bound below here: allowed (inclusive)
        if fallback is None:
            return None
        fP, fN, fh, fres = fallback
        return fres | self._extreme(fP, fN, fh - 1, x, big)


from bisect import bisect_left


# tree = Tree(edges, root, bits)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# bits: values live in [0, 2^bits).
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, bits)    # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, bits)    # nodes 1..3, rooted at 1
#
# An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
# between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the end
# farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns. Nodes
# go in and come out with your labels, -1 means "none", and a label that is not in the tree raises IndexError. Nothing
# recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Each edge's weight sits at its lower end's position in
# the range structure above (BitXorTries); the root's position holds no edge. The edges below node are one range of it,
# and the edges of a path a..b are O(log n) ranges, one per chain it crosses.
class Tree:
    # O(n * log n * log U) -- builds the layout and the range structure; raises ValueError when the edges are not one
    # tree on nodes 0..n-1 or 1..n, or an edge has no weight
    def __init__(self, edges, root, bits):
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
        self.seg = BitXorTries(arr, bits)  # each edge's weight, at its lower end's position

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.seg.pointGet(self._edge("edgeGet", a, b))

    # O(log n * log U) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.seg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log^2 n * log U) -- min edge weight on the path a..b; inf when a == b (no edges)
    def edgePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMin", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeMin
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

    # O(log^2 n * log U) -- max edge weight on the path a..b; -inf when a == b (no edges)
    def edgePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMax", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeMax
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

    # O(log^2 n * log U) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    def edgePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    def edgePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countLteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    def edgePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGtX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    def edgePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countGteX
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    def edgePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, low, high)
        return res

    # O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is >= x (None if none); None when a == b
    # (no edges)
    def edgePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v < res):
                res = v
        return res

    # O(log^2 n * log U) -- smallest of the edge weights on the path a..b that is > x (None if none); None when a == b
    # (no edges)
    def edgePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.smallestGtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v < res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v < res):
                res = v
        return res

    # O(log^2 n * log U) -- largest of the edge weights on the path a..b that is <= x (None if none); None when a == b
    # (no edges)
    def edgePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLteX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLteX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v > res):
                res = v
        return res

    # O(log^2 n * log U) -- largest of the edge weights on the path a..b that is < x (None if none); None when a == b
    # (no edges)
    def edgePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLtX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.largestLtX
        res = None
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v is not None and (res is None or v > res):
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v is not None and (res is None or v > res):
                res = v
        return res

    # O(log^2 n * log U) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    def edgePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countOccurrences
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(log^2 n * log U) -- largest weight ^ x over the edge weights on the path a..b; -inf when a == b (no edges)
    def edgePathMaxXorAgainstX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMaxXorAgainstX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.maxXorAgainstX
        res = float("-inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v > res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v > res:
                res = v
        return res

    # O(log^2 n * log U) -- smallest weight ^ x over the edge weights on the path a..b; inf when a == b (no edges)
    def edgePathMinXorAgainstX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMinXorAgainstX", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.minXorAgainstX
        res = float("inf")
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            v = query(pos[head[a]], pos[a], x)
            if v < res:
                res = v
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            v = query(l + 1, r, x)
            if v < res:
                res = v
        return res

    # O(log n * log U) -- min edge weight in node's subtree; inf when node is a leaf (no edges)
    def edgeSubtreeMin(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMin", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("inf")
        return self.seg.rangeMin(l, r)

    # O(log n * log U) -- max edge weight in node's subtree; -inf when node is a leaf (no edges)
    def edgeSubtreeMax(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMax", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("-inf")
        return self.seg.rangeMax(l, r)

    # O(log n * log U) -- kth smallest of the edge weights in node's subtree (1-indexed: k = 1 is the min); needs at
    # least one edge (not node is a leaf), else IndexError
    def edgeSubtreeKthSmallest(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeKthSmallest", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            raise IndexError("edgeSubtreeKthSmallest: needs at least one edge in node's subtree")
        return self.seg.kthSmallest(l, r, k)

    # O(log n * log U) -- how many edge weights in node's subtree are < x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountLtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countLtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are <= x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountLteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countLteX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are > x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountGtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countGtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are >= x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountGteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countGteX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no edges)
    def edgeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountInValRange", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countInValRange(l, r, low, high)

    # O(log n * log U) -- smallest of the edge weights in node's subtree that is >= x (None if none); None when node is
    # a leaf (no edges)
    def edgeSubtreeSmallestGteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSmallestGteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.seg.smallestGteX(l, r, x)

    # O(log n * log U) -- smallest of the edge weights in node's subtree that is > x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeSmallestGtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSmallestGtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.seg.smallestGtX(l, r, x)

    # O(log n * log U) -- largest of the edge weights in node's subtree that is <= x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeLargestLteX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeLargestLteX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.seg.largestLteX(l, r, x)

    # O(log n * log U) -- largest of the edge weights in node's subtree that is < x (None if none); None when node is a
    # leaf (no edges)
    def edgeSubtreeLargestLtX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeLargestLtX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return None
        return self.seg.largestLtX(l, r, x)

    # O(log n * log U) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountOccurrences", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.seg.countOccurrences(l, r, x)

    # O(log n * log U) -- largest weight ^ x over the edge weights in node's subtree; -inf when node is a leaf (no
    # edges)
    def edgeSubtreeMaxXorAgainstX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMaxXorAgainstX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("-inf")
        return self.seg.maxXorAgainstX(l, r, x)

    # O(log n * log U) -- smallest weight ^ x over the edge weights in node's subtree; inf when node is a leaf (no
    # edges)
    def edgeSubtreeMinXorAgainstX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMinXorAgainstX", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return float("inf")
        return self.seg.minXorAgainstX(l, r, x)

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
