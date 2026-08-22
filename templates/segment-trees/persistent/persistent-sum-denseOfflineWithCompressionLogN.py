# TEMPLATE BY ISHAANBUILDSTHINGS (see my github)
#
# EXAMPLE
#   vrs = StaticValueRangeSum(A)
#   s = vrs.sumValsInValRange(l, r, lowVal, highVal)  # lowVal <= A[i] <= highVal
#   t = vrs.sumValsLteX(l, r, X)                      # X need not appear in A
#   c = vrs.cntValsLtX(l, r, X)
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
    __slots__ = ('n', 'm', 'srt', 'root', 'L', 'R', 'S', 'C')

    # O(n log n)
    def __init__(self, A):
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
    def sumValsInValRange(self, l, r, lowVal, highVal):
        return self._ranks(l, r, self._lb(lowVal), self._ub(highVal) - 1)[0]

    def sumValsLteX(self, l, r, X): return self._ranks(l, r, 0, self._ub(X) - 1)[0]
    def sumValsLtX(self, l, r, X):  return self._ranks(l, r, 0, self._lb(X) - 1)[0]
    def sumValsGteX(self, l, r, X): return self._ranks(l, r, self._lb(X), self.m - 1)[0]
    def sumValsGtX(self, l, r, X):  return self._ranks(l, r, self._ub(X), self.m - 1)[0]
    def sumValsAll(self, l, r):     return self._ranks(l, r, 0, self.m - 1)[0]

    # ---- counts of how many such i ----
    # O(log n) -- lowVal <= A[i] <= highVal
    def cntValsInValRange(self, l, r, lowVal, highVal):
        return self._ranks(l, r, self._lb(lowVal), self._ub(highVal) - 1)[1]

    def cntValsLteX(self, l, r, X): return self._ranks(l, r, 0, self._ub(X) - 1)[1]
    def cntValsLtX(self, l, r, X):  return self._ranks(l, r, 0, self._lb(X) - 1)[1]
    def cntValsGteX(self, l, r, X): return self._ranks(l, r, self._lb(X), self.m - 1)[1]
    def cntValsGtX(self, l, r, X):  return self._ranks(l, r, self._ub(X), self.m - 1)[1]
    def cntValsAll(self, l, r):     return self._ranks(l, r, 0, self.m - 1)[1]

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