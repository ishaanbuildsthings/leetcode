# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-xor-or-table-and-tree/sparse.py
# @operations: andGtX andGteX andInValRange andLtX andLteX countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMin smallestGtX smallestGteX xorGtX xorGteX xorInValRange xorLtX xorLteX
# @data-structure-type: wavelet
# @complexities:
#   andGtX: log^2(N)
#   andGteX: log^2(N)
#   andInValRange: log^2(N)
#   andLtX: log^2(N)
#   andLteX: log^2(N)
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   countOccurrences: log(N)
#   kthSmallest: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   orGtX: log(N)
#   orGteX: log(N)
#   orInValRange: log(N)
#   orLtX: log(N)
#   orLteX: log(N)
#   pointGet: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
#   xorGtX: log(N)
#   xorGteX: log(N)
#   xorInValRange: log(N)
#   xorLtX: log(N)
#   xorLteX: log(N)
#   build: N*log^2(N)
# @memory:
#   layout: sparse
#   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] arr[1*N] srt[1*N] xt[1*N*log(N)] ot[1*N*log^2(N)] at[2*N*log(N)]
#   tags: none
#   other: none
#   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value; xor by value: per level, prefix xors of its order; OR by value: per level, a sparse table over its order (O(1) a window); AND by value: per level, a segment tree over its order (O(log N) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
from bisect import bisect_left, bisect_right
from itertools import accumulate
from operator import or_, xor


class WaveletMatrix:
    __slots__ = ('arr', 'n', 'srt', 'm', 'bits', 'zeros', 'xt', 'ot', 'at')

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
        self.xt = []  # per level, xor over its order
        self.ot = []  # per level, OR over its order
        self.at = []  # per level, AND over its order
        for d in range(bits - 1, -1, -1):
            self.xt.append(self._xorTab([srt[v] for v in cur]))
            self.ot.append(self._orTab([srt[v] for v in cur]))
            self.at.append(self._andTab([srt[v] for v in cur]))
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]
        self.xt.append(self._xorTab([srt[v] for v in cur]))  # (the final order)
        self.ot.append(self._orTab([srt[v] for v in cur]))  # (the final order)
        self.at.append(self._andTab([srt[v] for v in cur]))  # (the final order)

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

    # O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none
    def xorLtX(self, l, r, x):
        return self._xorRanks(l, r, 0, bisect_left(self.srt, x))

    # O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none
    def xorLteX(self, l, r, x):
        return self._xorRanks(l, r, 0, bisect_right(self.srt, x))

    # O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none
    def xorGtX(self, l, r, x):
        return self._xorRanks(l, r, bisect_right(self.srt, x), self.m)

    # O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none
    def xorGteX(self, l, r, x):
        return self._xorRanks(l, r, bisect_left(self.srt, x), self.m)

    # O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none
    def xorInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._xorRanks(l, r, bisect_left(self.srt, lowVal), bisect_right(self.srt, highVal))

    # O(logN) -- OR of the values < x in a[l..r]; 0 if there are none
    def orLtX(self, l, r, x):
        return self._orRanks(l, r, 0, bisect_left(self.srt, x))

    # O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none
    def orLteX(self, l, r, x):
        return self._orRanks(l, r, 0, bisect_right(self.srt, x))

    # O(logN) -- OR of the values > x in a[l..r]; 0 if there are none
    def orGtX(self, l, r, x):
        return self._orRanks(l, r, bisect_right(self.srt, x), self.m)

    # O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none
    def orGteX(self, l, r, x):
        return self._orRanks(l, r, bisect_left(self.srt, x), self.m)

    # O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none
    def orInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._orRanks(l, r, bisect_left(self.srt, lowVal), bisect_right(self.srt, highVal))

    # O(log^2 N) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    def andLtX(self, l, r, x):
        return self._andRanks(l, r, 0, bisect_left(self.srt, x))

    # O(log^2 N) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    def andLteX(self, l, r, x):
        return self._andRanks(l, r, 0, bisect_right(self.srt, x))

    # O(log^2 N) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    def andGtX(self, l, r, x):
        return self._andRanks(l, r, bisect_right(self.srt, x), self.m)

    # O(log^2 N) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    def andGteX(self, l, r, x):
        return self._andRanks(l, r, bisect_left(self.srt, x), self.m)

    # O(log^2 N) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
    def andInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return -1
        return self._andRanks(l, r, bisect_left(self.srt, lowVal), bisect_right(self.srt, highVal))

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

    @staticmethod
    def _xorTab(vals):  # prefix xors
        return list(accumulate(vals, xor, initial=0))

    def _xorQ(self, lv, lo, hi):  # xor of level lv's order at positions [lo, hi)
        t = self.xt[lv]
        return t[hi] ^ t[lo]

    # xor of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    def _xorRanks(self, l, r, a, b):
        res = 0
        if a >= b:
            return res
        bits, Z = self.bits, self.zeros
        stack = [(0, l, r + 1, 0)]  # (level, window [lo, hi) of its order, first rank under it)
        while stack:
            lv, lo, hi, nl = stack.pop()
            nr = nl + (1 << (bits - lv))
            if lo >= hi or nr <= a or b <= nl:
                continue
            if a <= nl and nr <= b:  # every rank under it counts: one window
                res ^= self._xorQ(lv, lo, hi)
                continue
            z = Z[lv]
            zl, zh = z[lo], z[hi]
            stack.append((lv + 1, zl, zh, nl))
            stack.append((lv + 1, z[-1] + lo - zl, z[-1] + hi - zh, nl + (1 << (bits - lv - 1))))
        return res

    @staticmethod
    def _orTab(vals):  # sparse table: row j = OR of every window of 2^j, in C-level passes
        rows, h = [vals], 1
        while 2 * h <= len(vals):
            p = rows[-1]
            rows.append(list(map(or_, p[:len(p) - h], p[h:])))
            h *= 2
        return rows

    def _orQ(self, lv, lo, hi):  # OR of level lv's order at positions [lo, hi), lo < hi
        rows = self.ot[lv]
        j = (hi - lo).bit_length() - 1
        return rows[j][lo] | rows[j][hi - (1 << j)]

    # OR of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    def _orRanks(self, l, r, a, b):
        res = 0
        if a >= b:
            return res
        bits, Z = self.bits, self.zeros
        stack = [(0, l, r + 1, 0)]  # (level, window [lo, hi) of its order, first rank under it)
        while stack:
            lv, lo, hi, nl = stack.pop()
            nr = nl + (1 << (bits - lv))
            if lo >= hi or nr <= a or b <= nl:
                continue
            if a <= nl and nr <= b:  # every rank under it counts: one window
                res |= self._orQ(lv, lo, hi)
                continue
            z = Z[lv]
            zl, zh = z[lo], z[hi]
            stack.append((lv + 1, zl, zh, nl))
            stack.append((lv + 1, z[-1] + lo - zl, z[-1] + hi - zh, nl + (1 << (bits - lv - 1))))
        return res

    @staticmethod
    def _andTab(vals):  # bottom-up segment tree: leaves at n..2n-1
        n = len(vals)
        t = [-1] * n + vals
        for i in range(n - 1, 0, -1):
            t[i] = t[2 * i] & t[2 * i + 1]
        return t

    def _andQ(self, lv, lo, hi):  # AND of level lv's order at positions [lo, hi)
        t, res = self.at[lv], -1
        lo += self.n
        hi += self.n
        while lo < hi:
            if lo & 1:
                res &= t[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res &= t[hi]
            lo >>= 1
            hi >>= 1
        return res

    # AND of the a[i], i in [l, r], whose rank is in [a, b): whole windows of the levels' orders
    def _andRanks(self, l, r, a, b):
        res = -1
        if a >= b:
            return res
        bits, Z = self.bits, self.zeros
        stack = [(0, l, r + 1, 0)]  # (level, window [lo, hi) of its order, first rank under it)
        while stack:
            lv, lo, hi, nl = stack.pop()
            nr = nl + (1 << (bits - lv))
            if lo >= hi or nr <= a or b <= nl:
                continue
            if a <= nl and nr <= b:  # every rank under it counts: one window
                res &= self._andQ(lv, lo, hi)
                continue
            z = Z[lv]
            zl, zh = z[lo], z[hi]
            stack.append((lv + 1, zl, zh, nl))
            stack.append((lv + 1, z[-1] + lo - zl, z[-1] + hi - zh, nl + (1 << (bits - lv - 1))))
        return res

# ======================================================================================== sparse wrapper

# The same queries over any index range [lo, hi], built from given values (index, value pairs); every other index is 0.
# The structure above runs on the given values alone (in index order). [l, r] covers given values i0..i1 and
# zeros = (r - l + 1) - (i1 - i0 + 1) zeros, and in sorted order those zeros sit right after the given negatives, so the
# k-th smallest of [l, r] is the given k-th while k <= neg, 0 while k <= neg + zeros, then the given (k - zeros)-th.

from bisect import bisect_left, bisect_right


class SparseWaveletMatrix:
    __slots__ = ("lo", "hi", "idx", "vals", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given values: (index, value) pairs with distinct indices; N = len(values)
    def __init__(self, lo, hi, values):
        self.lo, self.hi = lo, hi
        pts = sorted(values)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        self.inner = WaveletMatrix(self.vals or [0])  # (a dummy element when there are no given values; it is never queried)

    # (i0, i1, zeros): the given values inside [l, r] are i0..i1, and the rest of [l, r] is that many zeros
    def _span(self, l, r):
        i0, i1 = bisect_left(self.idx, l), bisect_right(self.idx, r) - 1
        return i0, i1, (r - l + 1) - (i1 - i0 + 1)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0

    # O(logN) -- # of i in [l, r] with a[i] == x
    def countOccurrences(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countOccurrences(i0, i1, x) if i0 <= i1 else 0) + (zeros if x == 0 else 0)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0
        return inside + (zeros if lowVal <= 0 <= highVal else 0)

    # O(logN) -- # of values < x in a[l..r]
    def countLtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countLtX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 < x else 0)

    # O(logN) -- # of values <= x in a[l..r]
    def countLteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countLteX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 <= x else 0)

    # O(logN) -- # of values > x in a[l..r]
    def countGtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countGtX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 > x else 0)

    # O(logN) -- # of values >= x in a[l..r]
    def countGteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countGteX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 >= x else 0)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallest(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]
    def rangeMin(self, l, r):
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]
    def rangeMax(self, l, r):
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None
    def smallestGteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        a = self.inner.smallestGteX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 >= x:
            a = 0 if a is None else min(a, 0)
        return a

    # O(logN) -- smallest value > x in a[l..r], or None
    def smallestGtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        a = self.inner.smallestGtX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 > x:
            a = 0 if a is None else min(a, 0)
        return a

    # O(logN) -- largest value <= x in a[l..r], or None
    def largestLteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        a = self.inner.largestLteX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 <= x:
            a = 0 if a is None else max(a, 0)
        return a

    # O(logN) -- largest value < x in a[l..r], or None
    def largestLtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        a = self.inner.largestLtX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 < x:
            a = 0 if a is None else max(a, 0)
        return a

    # O(logN) -- xor of the values < x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    def xorLtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.xorLtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- xor of the values <= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    def xorLteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.xorLteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- xor of the values > x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    def xorGtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.xorGtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- xor of the values >= x in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    def xorGteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.xorGteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- xor of the a[i] with lowVal <= a[i] <= highVal in a[l..r] (copies count); 0 if there are none (the zeros add nothing)
    def xorInValRange(self, l, r, lowVal, highVal):
        i0, i1, zeros = self._span(l, r)
        return self.inner.xorInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0

    # O(logN) -- OR of the values < x in a[l..r]; 0 if there are none (the zeros add nothing)
    def orLtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.orLtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none (the zeros add nothing)
    def orLteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.orLteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values > x in a[l..r]; 0 if there are none (the zeros add nothing)
    def orGtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.orGtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none (the zeros add nothing)
    def orGteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        return self.inner.orGteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none (the zeros add nothing)
    def orInValRange(self, l, r, lowVal, highVal):
        i0, i1, zeros = self._span(l, r)
        return self.inner.orInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0

    # O(logN) -- AND of the values < x in a[l..r]; -1 (every bit) if there are none
    def andLtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        if zeros and 0 < x:  # a 0 in range makes the AND 0
            return 0
        return self.inner.andLtX(i0, i1, x) if i0 <= i1 else -1

    # O(logN) -- AND of the values <= x in a[l..r]; -1 (every bit) if there are none
    def andLteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        if zeros and 0 <= x:  # a 0 in range makes the AND 0
            return 0
        return self.inner.andLteX(i0, i1, x) if i0 <= i1 else -1

    # O(logN) -- AND of the values > x in a[l..r]; -1 (every bit) if there are none
    def andGtX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        if zeros and 0 > x:  # a 0 in range makes the AND 0
            return 0
        return self.inner.andGtX(i0, i1, x) if i0 <= i1 else -1

    # O(logN) -- AND of the values >= x in a[l..r]; -1 (every bit) if there are none
    def andGteX(self, l, r, x):
        i0, i1, zeros = self._span(l, r)
        if zeros and 0 >= x:  # a 0 in range makes the AND 0
            return 0
        return self.inner.andGteX(i0, i1, x) if i0 <= i1 else -1

    # O(logN) -- AND of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; -1 (every bit) if there are none
    def andInValRange(self, l, r, lowVal, highVal):
        i0, i1, zeros = self._span(l, r)
        if zeros and lowVal <= 0 <= highVal:  # a 0 in range makes the AND 0
            return 0
        return self.inner.andInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else -1

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        i0, i1, zeros = self._span(l, r)
        neg = self.inner.countLtX(i0, i1, 0) if i0 <= i1 else 0
        if k <= neg:
            return self.inner.kthSmallest(i0, i1, k)
        if k <= neg + zeros:
            return 0
        return self.inner.kthSmallest(i0, i1, k - zeros)
