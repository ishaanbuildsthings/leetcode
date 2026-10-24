# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-order-stats-sums/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
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
#   rangeSum: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   sumAbsDiffToMedian: log(N)
#   sumAbsDiffToX: log(N)
#   sumGtX: log(N)
#   sumGteX: log(N)
#   sumInValRange: log(N)
#   sumKthLargestRange: log(N)
#   sumKthSmallestRange: log(N)
#   sumLargestK: log(N)
#   sumLtX: log(N)
#   sumLteX: log(N)
#   sumSmallestK: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[1*N*log(N)] R[1*N*log(N)] C[1*N*log(N)] S[1*N*log(N)]
#   tags: none
#   other: root[1*N] arr[1*N] srt[1*N]
#   note: persistent seg tree over the compressed values: about N log N nodes; L/R are child pointers, C counts, S sums

# Static array. Persistent seg tree over the values' compressed ranks: version p holds a[0..p-1], so a[l..r] is
# version r + 1 minus version l, and every query walks down those two versions together. Costs are log of the number
# of distinct values, never of the value range; query arguments (x, lowVal, ...) can be anything. 0-indexed, inclusive.
from bisect import bisect_left, bisect_right


class PersistentOrderStats:
    __slots__ = ('arr', 'n', 'srt', 'm', 'klo', 'khi', 'root', 'L', 'R', 'C', 'S')

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.srt = srt = sorted(set(arr))
        self.m = len(srt)
        self.klo, self.khi = 0, max(self.m - 1, 0)  # the tree is over ranks 0..m-1
        where = {v: k for k, v in enumerate(srt)}
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.S = [0]
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

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sumFirst(l, r, r - l + 1)

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._sumBelow(l, r, bisect_right(self.srt, highVal)) - self._sumBelow(l, r, bisect_left(self.srt, lowVal))

    # O(logN) -- sum of the values < x in a[l..r]
    def sumLtX(self, l, r, x):
        return self._sumBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- sum of the values <= x in a[l..r]
    def sumLteX(self, l, r, x):
        return self._sumBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- sum of the values > x in a[l..r]
    def sumGtX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- sum of the values >= x in a[l..r]
    def sumGteX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= k <= r - l + 1, else IndexError
    def sumLargestK(self, l, r, k):
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)

    # O(logN) -- sum of the i-th..j-th smallest values of a[l..r] (1-indexed, inclusive); needs 1 <= i <= j <= r - l + 1,
    # else IndexError
    def sumKthSmallestRange(self, l, r, i, j):
        if not 1 <= i <= j <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= i <= j <= r - l + 1, got i = {i}, j = {j}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, j) - self._sumFirst(l, r, i - 1)

    # O(logN) -- sum of the i-th..j-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest); needs
    # 1 <= i <= j <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, i, j):
        n = r - l + 1
        if not 1 <= i <= j <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= i <= j <= r - l + 1, got i = {i}, j = {j}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - i + 1) - self._sumFirst(l, r, n - j)

    # O(logN) -- sum of |a[i] - x| over i in [l, r]
    def sumAbsDiffToX(self, l, r, x):
        rk = bisect_left(self.srt, x)
        c, s = self._countBelow(l, r, rk), self._sumBelow(l, r, rk)
        return x * c - s + (self._sumFirst(l, r, r - l + 1) - s) - x * (r - l + 1 - c)

    # O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    def sumAbsDiffToMedian(self, l, r):
        return self.sumAbsDiffToX(l, r, self._kth(l, r, (r - l + 2) // 2))

    # ---- internals ----

    # copy of version node with one more value (key = its compressed rank)
    def _ins(self, node, key, v):
        L, R, C, S = self.L, self.R, self.C, self.S
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
        L.append(0), R.append(0), C.append(C[node] + 1), S.append(S[node] + v)
        for old, left in reversed(path):
            lc, rc = (cur, R[old]) if left else (L[old], cur)
            cur = len(C)
            L.append(lc), R.append(rc), C.append(C[lc] + C[rc]), S.append(S[lc] + S[rc])
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

    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        if k <= 0:
            return 0
        L, R, C, S = self.L, self.R, self.C, self.S
        a, b, nl, nh, res = self.root[r + 1], self.root[l], self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            c = C[L[a]] - C[L[b]]
            if k <= c:
                a, b, nh = L[a], L[b], mid
            else:  # the whole left half is among the k smallest
                k -= c
                res += S[L[a]] - S[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res + k * self.srt[nl]

    # sum of the a[i], i in [l, r], whose compressed rank is < x
    def _sumBelow(self, l, r, x):
        if x <= self.klo:
            return 0
        L, R, S = self.L, self.R, self.S
        a, b = self.root[r + 1], self.root[l]
        if x > self.khi:
            return S[a] - S[b]
        nl, nh, res = self.klo, self.khi, 0
        while nl != nh:
            mid = (nl + nh) >> 1
            if x <= mid:
                a, b, nh = L[a], L[b], mid
            else:
                res += S[L[a]] - S[L[b]]
                a, b, nl = R[a], R[b], mid + 1
        return res
