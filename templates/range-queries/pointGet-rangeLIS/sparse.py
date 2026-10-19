# @operations: pointGet rangeLIS
# @data-structure-type: merge-sort-tree
# @complexities:
#   pointGet: log(N)
#   rangeLIS: log(N)
#   build: N*log^2(N)
# @memory:
#   layout: sparse
#   node: cnt[2*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] starts[2*N] E[2*N] sortedVals[2*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; the seaweed LIS structure runs on the points plus one 0 per gap (at most 2N + 1 elements)
import sys
from bisect import bisect_right

# Static range LIS: length of the longest STRICTLY increasing subsequence of a[l..r], online, O(log N) per query.
# All indices 0-based, ranges inclusive.
#
# HOW IT WORKS (Tiskin's "seaweed" algorithm)
# Turn a into a permutation (equal values ranked right-to-left, so "strictly increasing" survives). Draw the grid
# rows = values, cols = positions, with a "match" at (a[j], j). Seaweeds enter from the left and the top and walk
# down / right; two seaweeds cross at a non-match cell unless they have already crossed, and never cross at a match.
# Let E[s] = the bottom column where the seaweed entering at top column s leaves (n if it leaves on the right). Then
#     LIS(a[l..r]) = (r - l + 1) - #{s in [l, n) : E[s] <= r}
# which is one 2D count. The braid of the whole grid is the "distance product" of the braids of its top and bottom
# halves (split by value), and that product takes O(n log n) with the "steady ant" walk, so the build is
# O(N log^2 N). Python handles N ~ 1e5 in tens of seconds; use the C++ version for big inputs.


def _dmul(P, Q):
    """Distance product of permutations: sigma_R(i,k) = min_j sigma_P(i,j) + sigma_Q(j,k), where
    sigma_X(i,k) = #{i' >= i : X[i'] < k}. Steady ant, O(n log n)."""
    n = len(P)
    if n == 1:
        return [0]
    m = n >> 1
    isLoCol = [False] * n
    for j in range(m):
        isLoCol[Q[j]] = True
    rank = [0] * n
    colsLo, colsHi = [], []
    for c in range(n):
        if isLoCol[c]:
            rank[c] = len(colsLo)
            colsLo.append(c)
        else:
            rank[c] = len(colsHi)
            colsHi.append(c)
    rowsLo, rowsHi, PLo, PHi = [], [], [], []
    for i in range(n):
        if P[i] < m:
            rowsLo.append(i)
            PLo.append(P[i])
        else:
            rowsHi.append(i)
            PHi.append(P[i] - m)
    RLo = _dmul(PLo, [rank[Q[j]] for j in range(m)])
    RHi = _dmul(PHi, [rank[Q[j]] for j in range(m, n)])
    rowIsLo = [False] * n
    rowCol = [0] * n
    colIsLoR = [False] * n
    colRow = [0] * n
    for t, i in enumerate(rowsLo):
        c = colsLo[RLo[t]]
        rowIsLo[i] = colIsLoR[c] = True
        rowCol[i], colRow[c] = c, i
    for t, i in enumerate(rowsHi):
        c = colsHi[RHi[t]]
        rowCol[i], colRow[c] = c, i
    # delta(i,k) = #lo(row >= i, col >= k) - #hi(row < i, col < k). R keeps lo points where delta >= 0 and hi
    # points where delta < 0; cells on the boundary between the two regions get fixed by the 2x2 formula below.
    # bnd(i) = first k with delta(i,k) < 0 (n + 1 if none); walking rows upward it only moves right.
    R = [0] * n
    k = d = 0
    while d >= 0:
        if k == n:
            k = n + 1
            break
        if not colIsLoR[k]:
            d -= 1
        k += 1
    bndBelow = k
    below = [0] * (n + 2)  # below[k] = delta(i+1, k) for k >= bnd(i+1)
    for i in range(n - 1, -1, -1):
        k0 = bndBelow
        if k0 == n + 1:
            bnd = n + 1
        else:
            dBelow = below[k0] = -1
            cur = 0 if (rowCol[i] >= k0) == rowIsLo[i] else -1
            k = k0
            while cur >= 0:
                if k == n:
                    k = n + 1
                    break
                r = colRow[k]
                if colIsLoR[k]:
                    if r >= i:
                        cur -= 1
                    if r >= i + 1:
                        dBelow -= 1
                else:
                    if r < i:
                        cur -= 1
                    if r < i + 1:
                        dBelow -= 1
                k += 1
                below[k] = dBelow
            bnd = k
        p, isLo = rowCol[i], rowIsLo[i]
        if (isLo and p + 1 < k0) or (not isLo and p >= bnd):
            R[i] = p
        else:
            for kk in range(max(0, k0 - 1), min(bnd - 1, n - 1) + 1):
                v = (1 if isLo and p == kk else 0) - (1 if kk + 1 == bnd else 0)
                if kk + 1 >= k0:
                    v -= below[kk + 1]
                if kk >= k0:
                    v += below[kk]
                if v == 1:
                    R[i] = kk
                    break
        bndBelow = bnd
    return R


def _braid(a):
    """Seaweed braid of the grid rows = values, cols = positions of permutation a. Size 2n: inputs are
    [left rows bottom->top | top cols], outputs are [bottom cols | right rows bottom->top]."""
    n = len(a)
    if n == 1:
        return [0, 1]
    m = n >> 1
    colsLo = [j for j in range(n) if a[j] < m]
    colsHi = [j for j in range(n) if a[j] >= m]

    def strip(cols, sub, k):
        # a k-row strip over all n columns; columns without a match in it pass straight down
        pi = [0] * (k + n)
        matched = [-1] * n
        for t, c in enumerate(cols):
            matched[c] = t
        for x in range(k):
            y = sub[x]
            pi[x] = cols[y] if y < k else n + y - k
        for j in range(n):
            t = matched[j]
            if t < 0:
                pi[k + j] = j
            else:
                y = sub[k + t]
                pi[k + j] = cols[y] if y < k else n + y - k
        return pi

    k1, k2 = m, n - m
    piT = strip(colsLo, _braid([a[j] for j in colsLo]), k1)
    piB = strip(colsHi, _braid([a[j] - m for j in colsHi]), k2)
    # stack the strips: extend each to all 2n seaweeds, then multiply (top strip first)
    T = list(range(k2)) + [k2 + y for y in piT]
    B = piB + [n + k2 + t for t in range(k1)]
    return _dmul(T, B)


class RangeLIS:
    __slots__ = ("arr", "n", "levels", "sortedVals", "cnt")

    # O(N log^2 N)
    def __init__(self, arr):
        sys.setrecursionlimit(max(10000, sys.getrecursionlimit()))
        self.arr = arr
        n = self.n = len(arr)
        self.levels = 0
        self.sortedVals = []
        self.cnt = []
        if n == 0:
            return
        order = sorted(range(n), key=lambda i: (arr[i], -i))  # equal values ranked right-to-left => strict LIS
        perm = [0] * n
        for rk, i in enumerate(order):
            perm[i] = rk
        pi = _braid(perm)
        E = [pi[n + s] if pi[n + s] < n else n for s in range(n)]
        # flat merge sort tree over E (fractional cascading, one row of prefix counts per level)
        levels = 0
        while (1 << levels) < n:
            levels += 1
        self.levels = levels
        cur = sorted(range(n), key=E.__getitem__)
        self.sortedVals = [E[i] for i in cur]
        buf = cur[:]
        nodes = [(0, n - 1)]
        for _ in range(levels):
            row = [0] * n
            nxt = []
            for tl, tr in nodes:
                if tl == tr:
                    continue
                mid = (tl + tr) >> 1
                lp, rp, run = tl, mid + 1, 0
                for j in range(tl, tr + 1):
                    idx = cur[j]
                    if idx <= mid:
                        buf[lp] = idx
                        lp += 1
                        run += 1
                    else:
                        buf[rp] = idx
                        rp += 1
                    row[j] = run
                nxt.append((tl, mid))
                nxt.append((mid + 1, tr))
            self.cnt.append(row)
            cur, buf = buf, cur
            nodes = nxt

    # O(logN) -- # of s in [ql, qr] with E[s] among the p smallest E values
    def _countPrefix(self, ql, qr, p):
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return p
            mid = (tl + tr) >> 1
            leftP = cnt[d][tl + p - 1] if p else 0
            if qr <= mid:
                tr, p = mid, leftP
            elif ql > mid:
                tl, p = mid + 1, p - leftP
            else:
                break
            d += 1
        res = 0
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            lp = cnt[da][a + pa - 1] if pa else 0
            if ql <= m:
                res += pa - lp
                b, pa = m, lp
            else:
                a, pa = m + 1, pa - lp
            da += 1
        res += pa
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            lp = cnt[da][a + pa - 1] if pa else 0
            if qr > m:
                res += lp
                a, pa = m + 1, pa - lp
            else:
                b, pa = m, lp
            da += 1
        return res + pa

    # O(logN) -- length of the longest strictly increasing subsequence of a[l..r]
    def rangeLIS(self, l, r):
        if l > r:
            return 0
        return (r - l + 1) - self._countPrefix(l, self.n - 1, bisect_right(self.sortedVals, r))

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Range LIS (longest strictly increasing subsequence; a run of zeros adds at most one element) over any index range [lo, hi], built from (index, value) points; every other index is 0. A maximal gap
# of zeros adds nothing more than a single 0, so RangeLIS runs on the compressed array of points with one 0 per gap,
# and a query maps l and r to the compressed elements containing them.


class SparseStaticLIS:
    __slots__ = ("lo", "hi", "idx", "vals", "starts", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        pts = sorted(points)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        starts, arr = [], []  # starts[k] = first index of compressed element k
        prev = lo - 1
        for i, v in pts:
            if i > prev + 1:
                starts.append(prev + 1)
                arr.append(0)
            starts.append(i)
            arr.append(v)
            prev = i
        if prev < hi:
            starts.append(prev + 1)
            arr.append(0)
        self.starts = starts
        self.inner = RangeLIS(arr)

    # O(logN) -- range lis of a[l..r]
    def rangeLIS(self, l, r):
        return self.inner.rangeLIS(bisect_right(self.starts, l) - 1, bisect_right(self.starts, r) - 1)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
