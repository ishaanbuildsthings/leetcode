# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/bit-of-tries-xor-sumxor/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences countXorGtK countXorGteK countXorLtK countXorLteK getAll kthSmallest kthXor largestLtX largestLteX largestXorLtK largestXorLteK maxAll maxXorAgainstX maxXorWithVGtM maxXorWithVGteM maxXorWithVInValRange maxXorWithVLtM maxXorWithVLteM minAll minXorAgainstX minXorWithVGtM minXorWithVGteM minXorWithVInValRange minXorWithVLtM minXorWithVLteM pointAssign pointGet rangeMax rangeMin rangeSum rangeXorQuery size smallestGtX smallestGteX smallestXorGtK smallestXorGteK sumXor
# @data-structure-type: bit-of-tries
# @complexities:
#   countGtX: log(N)*log(U)
#   countGteX: log(N)*log(U)
#   countInValRange: log(N)*log(U)
#   countLtX: log(N)*log(U)
#   countLteX: log(N)*log(U)
#   countOccurrences: log(N)*log(U)
#   countXorGtK: log(N)*log(U)
#   countXorGteK: log(N)*log(U)
#   countXorLtK: log(N)*log(U)
#   countXorLteK: log(N)*log(U)
#   getAll: N
#   kthSmallest: log(N)*log(U)
#   kthXor: log(N)*log(U)
#   largestLtX: log(N)*log(U)
#   largestLteX: log(N)*log(U)
#   largestXorLtK: log(N)*log(U)
#   largestXorLteK: log(N)*log(U)
#   maxAll: log(N)*log(U)
#   maxXorAgainstX: log(N)*log(U)
#   maxXorWithVGtM: log(N)*log(U)
#   maxXorWithVGteM: log(N)*log(U)
#   maxXorWithVInValRange: log(N)*log(U)
#   maxXorWithVLtM: log(N)*log(U)
#   maxXorWithVLteM: log(N)*log(U)
#   minAll: log(N)*log(U)
#   minXorAgainstX: log(N)*log(U)
#   minXorWithVGtM: log(N)*log(U)
#   minXorWithVGteM: log(N)*log(U)
#   minXorWithVInValRange: log(N)*log(U)
#   minXorWithVLtM: log(N)*log(U)
#   minXorWithVLteM: log(N)*log(U)
#   pointAssign: log(N)*log(U)
#   pointGet: 1
#   rangeMax: log(N)*log(U)
#   rangeMin: log(N)*log(U)
#   rangeSum: log(N)*log(U)
#   rangeXorQuery: log(N)*log(U)
#   size: 1
#   smallestGtX: log(N)*log(U)
#   smallestGteX: log(N)*log(U)
#   smallestXorGtK: log(N)*log(U)
#   smallestXorGteK: log(N)*log(U)
#   sumXor: log(N)*log(U)
#   build: N*log(N)*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(N)*log(U)] R[1*N*log(N)*log(U)] C[1*N*log(N)*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N] F[1*N*log(U)]
#   note: BIT over positions, each BIT node a binary trie of its block's values (U = 2^bits); nodes are never freed, so each point assign adds up to 2 log N log U of them

# a[l..r] as a multiset, asked about v ^ x over its values v, with point assigns. A Fenwick tree (BIT) over positions:
# BIT node j is a binary trie (one level per bit, highest bit first) of the values a[j - lowbit(j) .. j - 1]. The values
# of a[l..r] are the BIT prefix of r + 1 minus the prefix of l, so a query walks those ~2 log N tries down together
# (adding the first prefix's counts, subtracting the second's). Values and every x must lie in [0, 2^bits); thresholds
# (k, m, lo, hi) can be any integers. 0-indexed, inclusive.
# sumXor: a Fenwick tree per bit counting the values with that bit set.
# The plain order statistics (counts, k-th, min / max, predecessor / successor) are the same walks with x = 0.


class BitXorTries:
    __slots__ = ('B', 'top', 'n', 'arr', 'root', 'L', 'R', 'C', 'F')

    # O(N logN logU) -- arr: the initial values (a list), each in [0, 2^bits) (bits = 30 holds values up to 1073741823);
    # U = 2^bits
    def __init__(self, arr, bits):
        self.B, self.top = bits, (1 << bits) - 1
        self.n, self.arr = len(arr), list(arr)
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = empty
        self.root = [0] * (self.n + 1)  # root[j] = BIT node j's trie (1-indexed)
        for j in range(1, self.n + 1):
            self.root[j] = self._new()
        self.F = [[0] * (self.n + 1) for _ in range(bits)]
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

    # O(logN logU) -- sum of v ^ x over the values v in a[l..r]; needs 0 <= l <= r < size()
    def sumXor(self, l, r, x):
        self._span("sumXor", l, r)
        cnt, res = r - l + 1, 0
        for h, f in enumerate(self.F):
            ones, j = 0, r + 1
            while j:
                ones += f[j]
                j &= j - 1
            j = l
            while j:
                ones -= f[j]
                j &= j - 1
            res += (cnt - ones if x >> h & 1 else ones) << h
        return res

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
    # 1,
    # else IndexError
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

    # O(logN logU) -- a[l] + ... + a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeSum(self, l, r):
        self._rangeCheck("rangeSum", l, r)
        return self._sumAll(l, r)

    # O(logN logU) -- a[l] ^ ... ^ a[r]; needs 0 <= l <= r < size(), else IndexError
    def rangeXorQuery(self, l, r):
        self._rangeCheck("rangeXorQuery", l, r)
        return self._xorAll(l, r)

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
        for h in range(self.B):
            if v >> h & 1:
                f, j = self.F[h], i + 1
                while j <= n:
                    f[j] += d
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

    def _sumAll(self, l, r):
        return self.sumXor(l, r, 0)

    def _xorAll(self, l, r):  # each bit is set in an odd number of values
        res = 0
        for h, f in enumerate(self.F):
            ones, j = 0, r + 1
            while j:
                ones += f[j]
                j &= j - 1
            j = l
            while j:
                ones -= f[j]
                j &= j - 1
            res |= (ones & 1) << h
        return res

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
