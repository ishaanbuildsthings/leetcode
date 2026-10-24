# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-mex/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthLargest kthSmallest largestLtX largestLteX medianHigh medianLow pointGet rangeMax rangeMex rangeMin smallestGtX smallestGteX
# @data-structure-type: wavelet
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
#   rangeMex: log(N)
#   rangeMin: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: zeros[1*N*log(N)] arr[1*N] srt[1*N] mexRoot[1*N] ML[1*N*log(N)] MR[1*N*log(N)] MN[1*N*log(N)]
#   tags: none
#   other: none
#   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; rangeMex uses a persistent seg tree over the values 0..N+1 holding each value's last index

# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
# rangeMex: a persistent seg tree over the values 0..N+1; version p holds, per value, its last index before p (-1 if
# none). The mex of a[l..r] is the first value whose last index in version r + 1 is < l.
from bisect import bisect_left, bisect_right
from itertools import accumulate


class WaveletMatrix:
    __slots__ = ('arr', 'n', 'srt', 'm', 'bits', 'zeros', 'mexRoot', 'ML', 'MR', 'MN')

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        self.srt = srt = sorted(set(arr))
        self.m = m = len(srt)
        self.bits = bits = max(1, (m - 1).bit_length())
        where = {v: k for k, v in enumerate(srt)}
        cur = [where[v] for v in arr]
        self.zeros = []
        for d in range(bits - 1, -1, -1):
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]
        self._buildMex()

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

    # O(logN) -- smallest integer >= 0 that is not in a[l..r]
    def rangeMex(self, l, r):
        return self._mexFrom(l, r, 0)

    # ---- internals ----

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        lo, hi, rank, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if k <= zh - zl:  # enough 0s at this bit: the answer has it 0
                lo, hi = zl, zh
            else:
                k -= zh - zl
                rank |= 1 << d
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
        return self.srt[rank]

    # # of i in [l, r] whose rank is < x
    def _countBelow(self, l, r, x):
        if x <= 0:
            return 0
        if x >= self.m:
            return r - l + 1
        lo, hi, res, d = l, r + 1, 0, self.bits
        for z in self.zeros:
            d -= 1
            zl, zh = z[lo], z[hi]
            if (x >> d) & 1:  # everything with this bit 0 is below x; keep going among the 1s
                res += zh - zl
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
            else:
                lo, hi = zl, zh
        return res

    # persistent seg tree over the values 0..n+1: version p holds, per value, its last index before p (-1: none)
    def _buildMex(self):
        n = self.n
        self.ML, self.MR, self.MN = [0], [0], [-1]  # node 0 = the empty tree (every last index -1)
        self.mexRoot = root = [0] * (n + 1)
        for i, v in enumerate(self.arr):
            root[i + 1] = self._mexSet(root[i], v, i) if 0 <= v <= n + 1 else root[i]

    # O(logN) -- copy of node with value v's last index set to i
    def _mexSet(self, node, v, i):
        ML, MR, MN = self.ML, self.MR, self.MN
        path = []
        nl, nh = 0, self.n + 1
        while nl != nh:
            mid = (nl + nh) >> 1
            if v <= mid:
                path.append((node, True))
                node, nh = ML[node], mid
            else:
                path.append((node, False))
                node, nl = MR[node], mid + 1
        cur = len(MN)
        ML.append(0), MR.append(0), MN.append(i)
        for old, left in reversed(path):
            lc, rc = (cur, MR[old]) if left else (ML[old], cur)
            cur = len(MN)
            ML.append(lc), MR.append(rc), MN.append(min(MN[lc], MN[rc]))
        return cur

    # O(logN) -- smallest value >= s that is not in a[l..r]: the leftmost value >= s whose last index (as of r) is < l
    def _mexFrom(self, l, r, s):
        ML, MR, MN = self.ML, self.MR, self.MN
        stack = [(self.mexRoot[r + 1], 0, self.n + 1)]
        while stack:
            t, nl, nh = stack.pop()
            if nh < s or MN[t] >= l:  # nothing allowed here, or every value here is in a[l..r]
                continue
            if not t:  # no value here was ever seen
                return max(nl, s)
            if nl == nh:
                return nl
            mid = (nl + nh) >> 1
            stack.append((MR[t], mid + 1, nh))
            stack.append((ML[t], nl, mid))
        return self.n + 2  # (unreachable: the n + 2 values 0..n+1 can't all be in a[l..r])
