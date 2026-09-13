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
    def countInRange(self, ql, qr, valLow, valHigh):
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
    def findKthGteX(self, ql, qr, k, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, bisect_left(self.sortedVals, x)):
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
    def findKthLteX(self, ql, qr, k, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, bisect_right(self.sortedVals, x)):
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


# nearest index to the left that is strictly smaller than arr[i]
# -1 if none, pop while arr[st[-1]] >= arr[i]
def rightmostOnLeftLtNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] >= arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is smaller than or equal to arr[i]
# -1 if none, pop while arr[st[-1]] > arr[i]
def rightmostOnLeftLteNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] > arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is strictly greater than arr[i]
# -1 if none, pop while arr[st[-1]] <= arr[i]
def rightmostOnLeftGtNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] <= arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the left that is greater than or equal to arr[i]
# -1 if none, pop while arr[st[-1]] < arr[i]
def rightmostOnLeftGteNum(arr):
    n = len(arr)
    st = []
    res = [-1] * n
    for i in range(n):
        while st and arr[st[-1]] < arr[i]:
            st.pop()
        res[i] = st[-1] if st else -1
        st.append(i)
    return res

# nearest index to the right that is strictly smaller than arr[i]
# n if none, pop while arr[st[-1]] >= arr[i]
def leftmostOnRightLtNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] >= arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is smaller than or equal to arr[i]
# n if none, pop while arr[st[-1]] > arr[i]
def leftmostOnRightLteNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] > arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is strictly greater than arr[i]
# n if none, pop while arr[st[-1]] <= arr[i]
def leftmostOnRightGtNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] <= arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res

# nearest index to the right that is greater than or equal to arr[i]
# n if none, pop while arr[st[-1]] < arr[i]
def leftmostOnRightGteNum(arr):
    n = len(arr)
    st = []
    res = [n] * n
    for i in range(n - 1, -1, -1):
        while st and arr[st[-1]] < arr[i]:
            st.pop()
        res[i] = st[-1] if st else n
        st.append(i)
    return res


class Solution:
    def shadowPairs(self, nums: list[int]) -> int:
        seg = MergeSortTree(nums)
        onRight = leftmostOnRightLtNum(nums)
        return sum(seg.countGteX(i + 1, onRight[i] - 1, nums[i] + 1) for i in range(len(nums)))