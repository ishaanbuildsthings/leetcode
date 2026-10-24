# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-order-stats/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet rangeMax rangeMin smallestGtX smallestGteX
# @data-structure-type: persistent
# @complexities:
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   countOccurrences: log(N)
#   kthLargest: log(N)
#   kthSmallest: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   medianHigh: log(N)
#   medianLow: log(N)
#   pointGet: 1
#   rangeMax: log(N)
#   rangeMin: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)]
#   tags: none
#   other: root[1*N] arr[1*N] srt[1*N]
#   note: persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts

# Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
# version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
# of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
from bisect import bisect_left, bisect_right


class PersistentOrderStats:
    __slots__ = ('arr', 'n', 'srt', 'm', 'klo', 'khi', 'root', 'L', 'R', 'C')

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.srt = srt = sorted(set(arr))
        self.m = len(srt)
        self.klo, self.khi = 0, max(self.m - 1, 0)  # the tree is over ranks 0..m-1
        where = {v: k for k, v in enumerate(srt)}
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.root = [0]
        for v in arr:
            self.root.append(self._ins(self.root[-1], where[v], v))

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r, bisect_left(self.srt, lowVal))

    # O(logN) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        return self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        return self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, r - l + 2 - k)

    # O(logN) -- lower median of a[l..r]: its ceil(len / 2)-th smallest
    def medianLow(self, l, r):
        return self._kth(l, r, (r - l + 2) // 2)

    # O(logN) -- upper median of a[l..r]: its (floor(len / 2) + 1)-th smallest
    def medianHigh(self, l, r):
        return self._kth(l, r, (r - l + 1) // 2 + 1)

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None
    def smallestGteX(self, l, r, x):
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # ---- internals ----

    # copy of version node with one more value (key = its compressed rank)
    def _ins(self, node, key, v):
        L, R, C = self.L, self.R, self.C
        path = []
        nl, nh = self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            if key <= mid:
                path.append((node, True))
                node, nh = L[node], mid
            else:
                path.append((node, False))
                node, nl = R[node], mid + 1
        cur = len(C)
        L.append(0), R.append(0), C.append(C[node] + 1)
        for old, left in reversed(path):
            lc, rc = (cur, R[old]) if left else (L[old], cur)
            cur = len(C)
            L.append(lc), R.append(rc), C.append(C[lc] + C[rc])
        return cur

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1: walk version r + 1 minus version l
    def _kth(self, l, r, k):
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh = self.root[r + 1], self.root[l], self.klo, self.khi
        while nl != nh:
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:
                k -= c
                a, b, nl = R[a], R[b], mid + 1
        return self.srt[nl]

    # # of i in [l, r] whose compressed rank is < x
    def _countBelow(self, l, r, x):
        if x <= self.klo:
            return 0
        if x > self.khi:
            return r - l + 1
        L, R, C = self.L, self.R, self.C
        a, b, nl, nh, res = self.root[r + 1], self.root[l], self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                a, b, nh = L[a], L[b], mid
            else:  # the whole left half is below x
                res += C[L[a]] - C[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res
