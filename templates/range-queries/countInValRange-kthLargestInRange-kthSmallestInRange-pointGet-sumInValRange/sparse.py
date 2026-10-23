# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet-sumInValRange/sparse.py
# @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet sumInValRange
# @data-structure-type: persistent
# @complexities:
#   countInValRange: log(N)
#   kthLargestInRange: log(N)
#   kthSmallestInRange: log(N)
#   pointGet: log(N)
#   sumInValRange: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: L[1*N*log(N)] R[1*N*log(N)] S[1*N*log(N)] C[1*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] root[1*N] srt[1*N]
#   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; the persistent tree is over the given values only; zeros add to counts (never to sums) and sit between the negatives and the positives for a k-th
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

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Count / sum of the values in a value range and k-th smallest / largest, over any index range [lo, hi], built from given
# values (index, value pairs); every other index is 0. The persistent tree runs on the given values alone; the zeros of
# [l, r] (its length minus the given values inside) add to a count when 0 is in the value range, never to a sum, and
# sit between the given negatives and positives for a k-th.


class SparseStaticValueRangeSum:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        vals = self.vals or [0]  # (a dummy element when there are no given values; it is never queried)
        self.inner = StaticValueRangeSum(vals)

    # (i0, i1, zeros): the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)

    # O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    def countInValRange(self, l, r, valLow, valHigh):
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, valLow, valHigh) if i0 <= i1 else 0
        return inside + (zeros if valLow <= 0 <= valHigh else 0)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallestInRange: k = {k} is outside [1, {r - l + 1}]")
        i0, i1, zeros = self._span(l, r)
        neg = self.inner.countInValRange(i0, i1, float("-inf"), -1) if i0 <= i1 else 0
        if k <= neg:
            return self.inner.kthSmallestInRange(i0, i1, k)
        if k <= neg + zeros:
            return 0
        return self.inner.kthSmallestInRange(i0, i1, k - zeros)

    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargestInRange: k = {k} is outside [1, {r - l + 1}]")
        return self.kthSmallestInRange(l, r, r - l + 2 - k)

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        i0, i1, _ = self._span(l, r)
        return self.inner.sumInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
