# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/persistent-online-order-stats-sums/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet pushBack rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToMedian sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: persistent
# @complexities:
#   countGtX: log(U)
#   countGteX: log(U)
#   countInValRange: log(U)
#   countLtX: log(U)
#   countLteX: log(U)
#   countOccurrences: log(U)
#   kthLargest: log(U)
#   kthSmallest: log(U)
#   largestLtX: log(U)
#   largestLteX: log(U)
#   medianHigh: log(U)
#   medianLow: log(U)
#   pointGet: 1
#   pushBack: log(U)
#   rangeMax: log(U)
#   rangeMin: log(U)
#   rangeSum: log(U)
#   smallestGtX: log(U)
#   smallestGteX: log(U)
#   sumAbsDiffToMedian: log(U)
#   sumAbsDiffToX: log(U)
#   sumGtX: log(U)
#   sumGteX: log(U)
#   sumInValRange: log(U)
#   sumKthLargestRange: log(U)
#   sumKthSmallestRange: log(U)
#   sumLargestK: log(U)
#   sumLtX: log(U)
#   sumLteX: log(U)
#   sumSmallestK: log(U)
#   build: N*log(U)
# @memory:
#   layout: none
#   node: L[1*N*log(U)] R[1*N*log(U)] C[1*N*log(U)] S[1*N*log(U)]
#   tags: none
#   other: root[1*N] arr[1*N]
#   note: N = every value ever added (initial array plus each pushBack); each adds one root-to-leaf path of log U nodes over the value range [valLo, valHi]

# An array that grows: pushBack(v) appends, and queries on any a[l..r] can come in between. Nothing is known up
# front, so the persistent seg tree is over the value range [valLo, valHi]: version p holds a[0..p-1], a[l..r] is
# version r + 1 minus version l, and each append adds one version. Values are integers; query arguments (x, lowVal,
# ...) can be anything. 0-indexed, inclusive.


class PersistentOnlineOrderStats:
    __slots__ = ('arr', 'n', 'klo', 'khi', 'root', 'L', 'R', 'C', 'S')

    # O(N log U) -- arr: the initial array (a list, may be empty), 0-indexed; every value ever added must lie in
    # [valLo, valHi] (any integers, negative is fine; U = valHi - valLo + 1)
    def __init__(self, arr, valLo, valHi):
        self.arr, self.n = [], 0
        self.klo, self.khi = valLo, valHi
        self.L, self.R, self.C = [0], [0], [0]  # node 0 = the empty tree
        self.S = [0]
        self.root = [0]
        for v in arr:
            self.pushBack(v)

    # O(logU) -- append v (valLo <= v <= valHi): it becomes a[n], and n grows by 1
    def pushBack(self, v):
        self.root.append(self._ins(self.root[-1], v, v))
        self.arr.append(v)
        self.n += 1

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
        return self._countBelow(l, r, highVal + 1) - self._countBelow(l, r, lowVal)

    # O(logN) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        return self._countBelow(l, r, x)

    # O(logN) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        return self._countBelow(l, r, x + 1)

    # O(logN) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, x + 1)

    # O(logN) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        return r - l + 1 - self._countBelow(l, r, x)

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
        c = self._countBelow(l, r, x)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        c = self._countBelow(l, r, x + 1)
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        c = self._countBelow(l, r, x + 1)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        c = self._countBelow(l, r, x)
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- a[l] + ... + a[r]
    def rangeSum(self, l, r):
        return self._sumFirst(l, r, r - l + 1)

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal
    def sumInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._sumBelow(l, r, highVal + 1) - self._sumBelow(l, r, lowVal)

    # O(logN) -- sum of the values < x in a[l..r]
    def sumLtX(self, l, r, x):
        return self._sumBelow(l, r, x)

    # O(logN) -- sum of the values <= x in a[l..r]
    def sumLteX(self, l, r, x):
        return self._sumBelow(l, r, x + 1)

    # O(logN) -- sum of the values > x in a[l..r]
    def sumGtX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, x + 1)

    # O(logN) -- sum of the values >= x in a[l..r]
    def sumGteX(self, l, r, x):
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, x)

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
        rk = x
        c, s = self._countBelow(l, r, rk), self._sumBelow(l, r, rk)
        return x * c - s + (self._sumFirst(l, r, r - l + 1) - s) - x * (r - l + 1 - c)

    # O(logN) -- sum of |a[i] - medianLow(l, r)| over i in [l, r]: the min total +-1 moves to make a[l..r] all equal
    def sumAbsDiffToMedian(self, l, r):
        return self.sumAbsDiffToX(l, r, self._kth(l, r, (r - l + 2) // 2))

    # ---- internals ----

    # copy of version node with one more value (key = its value)
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
        return nl

    # # of i in [l, r] whose value is < x
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
        return res + k * nl

    # sum of the a[i], i in [l, r], whose value is < x
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
