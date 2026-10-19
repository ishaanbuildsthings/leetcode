# @operations: countDistinct countInValRange kthGtX kthGteX kthLtX kthLteX pointGet
# @data-structure-type: merge-sort-tree
# @complexities:
#   countDistinct: log(N)
#   countInValRange: log(N)
#   kthGtX: log(N)
#   kthGteX: log(N)
#   kthLtX: log(N)
#   kthLteX: log(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: cnt[2*N*log(N)]
#   tags: none
#   other: sortedVals[2*N] nxt[1*N]
#   note: two flat merge sort trees (one row of N prefix counts per level): one over the values for count / kth, one over nxt[i] for countDistinct
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/merge/rangeDistinct_LogN_NoUpdates.py

# TEMPLATE BY ishaanbuildsthings github
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
