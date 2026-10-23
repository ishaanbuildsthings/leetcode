# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet-sumInValRange/template.py
# @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet sumInValRange
# @data-structure-type: persistent
# @complexities:
#   countInValRange: log(N)
#   kthLargestInRange: log(N)
#   kthSmallestInRange: log(N)
#   pointGet: 1
#   sumInValRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[1*N*log(N)] R[1*N*log(N)] S[1*N*log(N)] C[1*N*log(N)]
#   tags: none
#   other: root[1*N] srt[1*N]
#   note: about N*log(N) persistent nodes; L/R are child pointers, S/C are sum and count
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/persistent/persistent-sum-denseOfflineWithCompressionLogN.py

# EXAMPLE
#   vrs = StaticValueRangeSum(A)
#   s = vrs.sumInValRange(l, r, lowVal, highVal)  # lowVal <= A[i] <= highVal
#   t = vrs.sumValsLteX(l, r, X)                      # X need not appear in A
#   c = vrs.cntValsLtX(l, r, X)
#   v = vrs.kthSmallestInRange(l, r, k)              # k = 1 is the min of A[l..r]
#
# Static array, offline or online queries. Values are compressed once in the
# constructor; query bounds are bisected into the compressed domain, so nothing
# depends on the value magnitude -- all costs are log n, not log U.
#
# Persistent sum segtree over value ranks; version p = histogram of A[0..p-1].
# Index range [l,r] comes from subtracting versions r+1 and l; the value window
# comes from the tree query. Index range always inclusive. Empty/inverted
# ranges return 0.
#
# Naming: sumVals* adds up the A[i] themselves, cntVals* counts how many there
# are. Lte/Gte are inclusive, Lt/Gt strict. InValRange is inclusive both ends.
#
# Python ints don't overflow, so value bounds can be any size -- pass an
# accumulated sum directly. Build and query are both iterative (no recursion).
#
# Build O(n log n) time and nodes. Query O(log n). Four parallel lists of
# n*ceil(log2 m) entries; n = 2e5 is ~3.6M nodes and a few hundred MB of Python
# ints -- swap L/R/C to array('i') if that's tight, or delete C/cntVals*.
from bisect import bisect_left, bisect_right


class StaticValueRangeSum:
    __slots__ = ('arr', 'n', 'm', 'srt', 'root', 'L', 'R', 'S', 'C')

    # O(n log n)
    def __init__(self, A):
        self.arr = A
        self.n = n = len(A)
        self.srt = srt = sorted(set(A))
        self.m = m = len(srt)
        self.L = [0]            # node 0 = null
        self.R = [0]
        self.S = [0]
        self.C = [0]
        self.root = [0] * (n + 1)
        if m == 0:
            return
        for i, v in enumerate(A):
            self.root[i + 1] = self._add(self.root[i], bisect_left(srt, v), v)

    # ---- sums of the values themselves, over i in [l,r] ----
    # O(log n) -- lowVal <= A[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        return self._ranks(l, r, self._lb(lowVal), self._ub(highVal) - 1)[0]

    def sumValsLteX(self, l, r, X): return self._ranks(l, r, 0, self._ub(X) - 1)[0]
    def sumValsLtX(self, l, r, X):  return self._ranks(l, r, 0, self._lb(X) - 1)[0]
    def sumValsGteX(self, l, r, X): return self._ranks(l, r, self._lb(X), self.m - 1)[0]
    def sumValsGtX(self, l, r, X):  return self._ranks(l, r, self._ub(X), self.m - 1)[0]
    def sumValsAll(self, l, r):     return self._ranks(l, r, 0, self.m - 1)[0]

    # ---- counts of how many such i ----
    # O(log n) -- lowVal <= A[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        return self._ranks(l, r, self._lb(lowVal), self._ub(highVal) - 1)[1]

    def cntValsLteX(self, l, r, X): return self._ranks(l, r, 0, self._ub(X) - 1)[1]
    def cntValsLtX(self, l, r, X):  return self._ranks(l, r, 0, self._lb(X) - 1)[1]
    def cntValsGteX(self, l, r, X): return self._ranks(l, r, self._lb(X), self.m - 1)[1]
    def cntValsGtX(self, l, r, X):  return self._ranks(l, r, self._ub(X), self.m - 1)[1]
    def cntValsAll(self, l, r):     return self._ranks(l, r, 0, self.m - 1)[1]

    # ---- k-th smallest / largest value of a[l..r] ----
    # O(log n) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallestInRange: k = {k} is outside [1, {r - l + 1}]")
        L, R, C = self.L, self.R, self.C
        a, b = self.root[r + 1], self.root[l]
        nl, nh = 0, self.m - 1
        while nl != nh:  # walk down version r+1 minus version l: the left child holds the smaller ranks
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:
                k -= c
                a, b, nl = R[a], R[b], mid + 1
        return self.srt[nl]

    # O(log n) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargestInRange: k = {k} is outside [1, {r - l + 1}]")
        return self.kthSmallestInRange(l, r, r - l + 2 - k)

    # first rank with value >= v
    def _lb(self, v): return bisect_left(self.srt, v)

    # first rank with value > v
    def _ub(self, v): return bisect_right(self.srt, v)

    # O(log n) -- walk down recording the path, then rebuild it leaf-up
    def _add(self, node, rk, w):
        L, R, S, C = self.L, self.R, self.S, self.C
        path = []
        nl, nh = 0, self.m - 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if rk <= mid:
                path.append((node, True))
                node = L[node]
                nh = mid
            else:
                path.append((node, False))
                node = R[node]
                nl = mid + 1
        cur = len(S)
        L.append(0); R.append(0); S.append(S[node] + w); C.append(C[node] + 1)
        for old, goLeft in reversed(path):
            lc, rc = L[old], R[old]
            if goLeft: lc = cur
            else:      rc = cur
            cur = len(S)
            L.append(lc); R.append(rc); S.append(S[lc] + S[rc]); C.append(C[lc] + C[rc])
        return cur

    # rank window already resolved; diff versions r+1 and l
    def _ranks(self, l, r, lo, hi):
        if self.m == 0 or l > r or l < 0 or r >= self.n or lo > hi:
            return (0, 0)
        L, R, S, C = self.L, self.R, self.S, self.C
        s = c = 0
        stack = [(self.root[r + 1], self.root[l], 0, self.m - 1)]
        while stack:
            a, b, nl, nh = stack.pop()
            if nh < lo or hi < nl:
                continue
            if lo <= nl and nh <= hi:
                s += S[a] - S[b]
                c += C[a] - C[b]
                continue
            mid = (nl + nh) >> 1
            stack.append((L[a], L[b], nl, mid))
            stack.append((R[a], R[b], mid + 1, nh))
        return (s, c)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]