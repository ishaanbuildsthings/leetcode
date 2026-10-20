# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countDistinct-countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet/sparse.py
# @operations: countDistinct countInValRange kthGtX kthGteX kthLtX kthLteX pointGet
# @data-structure-type: merge-sort-tree
# @complexities:
#   countDistinct: log(N)
#   countInValRange: log(N)
#   kthGtX: log^2(N)
#   kthGteX: log^2(N)
#   kthLtX: log^2(N)
#   kthLteX: log^2(N)
#   pointGet: log(N)
#   build: N*log(N)
# @memory:
#   layout: sparse
#   node: cnt[2*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] sortedVals[2*N] nxt[1*N] zc[1*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; both merge sort trees are over the points only; zeros add one distinct value when [l, r] has a zero and no point holding 0 (zc counts those points)
from bisect import bisect_left, bisect_right
from itertools import accumulate, compress
from operator import not_


class MergeSortTree:
    # Build: O(n log n) time, ceil(log2 n) * n ints of space.
    # Every query: O(log n) — one binary search at the root, then an iterative
    # top-down walk, O(1) per level, no recursion and no per-node lists.
    #
    # Same two representational choices as the C++ template:
    #   * Nodes do not store their sorted values. Fractional cascading only ever
    #     binary searches the root, so only sortedVals is kept. A node's element
    #     count is tr - tl + 1, which the walk already tracks.
    #   * cnt is one row per depth. At any depth the segment tree nodes partition
    #     [0, n-1], and a node covering [tl, tr] owns exactly working-array slots
    #     tl..tr, so (depth, tl) addresses a node's prefix data with no offset
    #     table and no node index at all.
    #
    # Divergences from the C++, all forced by CPython:
    #   * cnt is a list of per-depth rows rather than one flat array with d * n
    #     offsets — same addressing, one less multiply per access.
    #   * leftCount is inlined at every use. As a method it would be ~34 calls
    #     per query and would dominate the query cost.
    #   * A size-2 node is special-cased in the build: both its children are
    #     leaves, so it needs no partition and no scratch writes. Saves half the
    #     internal nodes. In C++ this is noise; here it is worth ~20% of the build.
    #   * sorted() instead of a radix sort — sorted() is already C, and a radix
    #     written in Python bytecode would be far slower.
    def __init__(self, arr):
        self.arr = arr
        self.n = n = len(arr)
        self.levels = levels = 0
        self.sortedVals = sorted(arr)  # root's sorted values — the only list ever binary-searched
        self.cnt = cnt = []            # cnt[d][tl + j] = # of the first (j+1) elements of the depth-d node starting at tl that live in its left child
        if n == 0:
            return
        width = 1
        while width < n:
            width <<= 1
            levels += 1
        self.levels = levels

        # Splitting a value-ordered index list on "index <= mid" preserves the
        # ordering, so each level is one stable partition per node — all C-level,
        # no merging.
        cur = sorted(range(n), key=arr.__getitem__)  # indices by value, ties by index — same tie rule as L[li] <= R[ri]
        buf = cur[:]
        nodes = [(0, n - 1)]
        for d in range(levels):
            row = [0] * n
            nxt = []
            addChild = nxt.append
            for tl, tr in nodes:
                span = tr - tl
                if span == 0:
                    continue
                if span == 1:
                    # both children are leaves, so they need no cnt row of their
                    # own and this node's two entries are fully determined by
                    # which of the two indices sorted first
                    if cur[tl] == tl:
                        row[tl] = 1
                    row[tr] = 1
                    continue
                mid = (tl + tr) >> 1
                seg = cur[tl:tr + 1]
                goesLeft = list(map(mid.__ge__, seg))  # True where index <= mid
                row[tl:tr + 1] = accumulate(goesLeft)
                buf[tl:mid + 1] = compress(seg, goesLeft)
                buf[mid + 1:tr + 1] = compress(seg, map(not_, goesLeft))
                addChild((tl, mid))
                addChild((mid + 1, tr))
            cnt.append(row)
            cur, buf = buf, cur
            nodes = nxt

    # --- count ---

    # O(log n) — count elements >= x in [ql, qr]
    # Seeded with bisect_left (elements < x) and complemented against the range size.
    # The walk is inlined rather than shared with countLteX: a countPrefix call
    # per query is measurable in CPython, and it is not in C++.
    def countGteX(self, ql, qr, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr:
            return 0
        total = qr - ql + 1
        p = bisect_left(self.sortedVals, x)
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return total - p
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break
        res = 0

        # left boundary: cover [ql, mid] inside the left child
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                res += pa - lp  # entire right child is inside [ql, qr]
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        res += pa

        # right boundary: cover [mid + 1, qr] inside the right child
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                res += lp  # entire left child is inside [ql, qr]
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        return total - (res + pa)

    # O(log n) — count elements <= x in [ql, qr]
    # Walk inlined, see countGteX
    def countLteX(self, ql, qr, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr:
            return 0
        p = bisect_right(self.sortedVals, x)
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return p
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break
        res = 0

        # left boundary: cover [ql, mid] inside the left child
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                res += pa - lp  # entire right child is inside [ql, qr]
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        res += pa

        # right boundary: cover [mid + 1, qr] inside the right child
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                res += lp  # entire left child is inside [ql, qr]
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        return res + pa

    # O(log n) — count elements in value range [valLow, valHigh] (inclusive) in index range [ql, qr]
    def countInValRange(self, ql, qr, valLow, valHigh):
        return self.countLteX(ql, qr, valHigh) - self.countLteX(ql, qr, valLow - 1)

    # --- find k-th by position ---

    # Same decomposition as countPrefix, but returns the canonical nodes in
    # LEFT-TO-RIGHT order as (d, tl, tr, p). At most 2 * levels + 2 of them.
    # Only findKth* needs this; the counting path stays allocation-free.
    def decompose(self, ql, qr, p):
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return [(d, tl, tr, p)]
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break

        # left walk collects right-to-left (the node it lands on is the leftmost), so reverse
        leftParts = []
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                leftParts.append((da + 1, m + 1, b, pa - lp))
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        leftParts.append((da, a, b, pa))
        parts = leftParts[::-1]

        # right walk already collects left-to-right
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                parts.append((da + 1, a, m, lp))
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        parts.append((da, a, b, pa))
        return parts

    # O(log n) — array index (POSITION, not value) of the k-th element >= x in
    # [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    # k-th (1-indexed, left to right) i in [ql, qr] NOT among the p0 globally-smallest values
    def _kthAbove(self, ql, qr, k, p0):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, p0):
            gteInNode = (tr - tl + 1) - p
            if k > gteInNode:
                k -= gteInNode
                continue
            while tl < tr:
                mid = (tl + tr) >> 1
                row = cnt[d]
                lp = row[tl + p - 1] if p else 0
                leftGte = (mid - tl + 1) - lp
                if k <= leftGte:
                    tr = mid
                    p = lp
                else:
                    k -= leftGte
                    tl = mid + 1
                    p -= lp
                d += 1
            return tl
        return -1

    # O(log n) — array index (POSITION, not value) of the k-th element <= x in
    # [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    # k-th (1-indexed, left to right) i in [ql, qr] among the p0 globally-smallest values
    def _kthBelow(self, ql, qr, k, p0):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, p0):
            if k > p:
                k -= p
                continue
            while tl < tr:
                mid = (tl + tr) >> 1
                row = cnt[d]
                lp = row[tl + p - 1] if p else 0
                if k <= lp:
                    tr = mid
                    p = lp
                else:
                    k -= lp
                    tl = mid + 1
                    p -= lp
                d += 1
            return tl
        return -1

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] >= x, or -1
    def kthGteX(self, ql, qr, k, x):
        return self._kthAbove(ql, qr, k, bisect_left(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] > x, or -1
    def kthGtX(self, ql, qr, k, x):
        return self._kthAbove(ql, qr, k, bisect_right(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] <= x, or -1
    def kthLteX(self, ql, qr, k, x):
        return self._kthBelow(ql, qr, k, bisect_right(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] < x, or -1
    def kthLtX(self, ql, qr, k, x):
        return self._kthBelow(ql, qr, k, bisect_left(self.sortedVals, x))

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]


class StaticDistinct:
    # Built on the MergeSortTree above, over nxt[] instead of the values.
    # Range count distinct, no updates. O(n log n) build, O(log n) query.
    # nxt[i] = next index j > i with a[j] == a[i], else n.
    # A value is counted once per window, at its LAST occurrence: nxt[i] > r.
    # Values may be any hashable type — nxt holds indices, so no compression.
    def __init__(self, arr):
        self.arr = arr
        n = len(arr)
        nxt = [n] * n
        last = {}
        for i in range(n - 1, -1, -1):
            nxt[i] = last.get(arr[i], n)
            last[arr[i]] = i
        self.mst = MergeSortTree(nxt)

    # O(log n) — # of distinct values in a[l..r], inclusive, 0-indexed
    def countDistinct(self, l, r):
        return self.mst.countGteX(l, r, r + 1)

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Count values in a value range / k-th index whose value passes a test, over any index range [lo, hi], built
# from (index, value) points; every other index is 0. The merge sort tree runs on the points alone; the zeros
# of [l, r] are its length minus the points inside, and they count wherever 0 passes the test.
# Distinct values: the points' distinct values, plus 0 if [l, r] has a zero index and no point holding 0.


class SparseStaticMergeSortTree:
    __slots__ = ("lo", "hi", "idx", "vals", "inner", "distinct", "zc")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        pts = sorted(points)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        vals = self.vals or [0]  # (a dummy element when there are no points; it is never queried)
        self.inner = MergeSortTree(vals)
        self.distinct = StaticDistinct(vals)
        self.zc = [0]  # zc[k] = # of the first k points holding 0
        for v in self.vals:
            self.zc.append(self.zc[-1] + (v == 0))

    # (i0, i1, zeros): the points inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)

    # O(logN) -- # of i in [l, r] with valLow <= a[i] <= valHigh
    def countInValRange(self, l, r, valLow, valHigh):
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, valLow, valHigh) if i0 <= i1 else 0
        return inside + (zeros if valLow <= 0 <= valHigh else 0)

    # O(logN) -- # of distinct values in a[l..r]
    def countDistinct(self, l, r):
        i0, i1, zeros = self._span(l, r)
        if i0 > i1:
            return 1
        return self.distinct.countDistinct(i0, i1) + (zeros > 0 and self.zc[i1 + 1] == self.zc[i0])

    # the k-th i in [l, r] whose value passes (test); qual(t) = qualifying points among i0..t-1; zeroOk: 0 passes
    def _kth(self, l, r, k, zeroOk, qual, denseKth):
        i0, i1, _ = self._span(l, r)
        if k <= 0:
            return self.lo - 1
        if not zeroOk:
            if k > i1 - i0 + 1:
                return self.lo - 1
            j = denseKth(i0, i1, k)
            return self.idx[j] if j != -1 else self.lo - 1
        idx = self.idx

        def g(t):  # qualifying indices in [l, (point t) - 1]; point i1 + 1 stands for r + 1
            return ((idx[t] if t <= i1 else r + 1) - l) - (t - i0) + qual(t)

        if g(i1 + 1) < k:
            return self.lo - 1
        a, b = i0, i1 + 1  # smallest t with g(t) >= k
        while a < b:
            m = (a + b) // 2
            if g(m) >= k:
                b = m
            else:
                a = m + 1
        t = a
        if t == i0:
            return l - 1 + k
        c = g(t - 1) + qual(t) - qual(t - 1)  # qualifying indices in [l, point t - 1]
        return idx[t - 1] if c >= k else idx[t - 1] + (k - c)

    # O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] >= x, or lo - 1
    def kthGteX(self, l, r, k, x):
        i0 = bisect_left(self.idx, l)
        return self._kth(l, r, k, 0 >= x, lambda t: self.inner.countGteX(i0, t - 1, x) if t > i0 else 0,
                         lambda a, b, kk: self.inner.kthGteX(a, b, kk, x))

    # O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] > x, or lo - 1
    def kthGtX(self, l, r, k, x):
        i0 = bisect_left(self.idx, l)
        return self._kth(l, r, k, 0 > x, lambda t: self.inner.countGteX(i0, t - 1, x + 1) if t > i0 else 0,
                         lambda a, b, kk: self.inner.kthGtX(a, b, kk, x))

    # O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] <= x, or lo - 1
    def kthLteX(self, l, r, k, x):
        i0 = bisect_left(self.idx, l)
        return self._kth(l, r, k, 0 <= x, lambda t: self.inner.countLteX(i0, t - 1, x) if t > i0 else 0,
                         lambda a, b, kk: self.inner.kthLteX(a, b, kk, x))

    # O(log^2 N) -- index of the k-th (1-indexed) i in [l, r] with a[i] < x, or lo - 1
    def kthLtX(self, l, r, k, x):
        i0 = bisect_left(self.idx, l)
        return self._kth(l, r, k, 0 < x, lambda t: self.inner.countLteX(i0, t - 1, x - 1) if t > i0 else 0,
                         lambda a, b, kk: self.inner.kthLtX(a, b, kk, x))

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
