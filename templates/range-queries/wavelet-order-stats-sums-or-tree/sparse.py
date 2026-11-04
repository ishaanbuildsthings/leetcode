# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/wavelet-order-stats-sums-or-tree/sparse.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX orGtX orGteX orInValRange orLtX orLteX pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
# @data-structure-type: wavelet
# @complexities:
#   countGtX: log(N)
#   countGteX: log(N)
#   countInValRange: log(N)
#   countLtX: log(N)
#   countLteX: log(N)
#   countOccurrences: log(N)
#   kthSmallest: log(N)
#   largestLtX: log(N)
#   largestLteX: log(N)
#   orGtX: log^2(N)
#   orGteX: log^2(N)
#   orInValRange: log^2(N)
#   orLtX: log^2(N)
#   orLteX: log^2(N)
#   pointGet: log(N)
#   rangeMax: log(N)
#   rangeMin: log(N)
#   rangeSum: log(N)
#   smallestGtX: log(N)
#   smallestGteX: log(N)
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
#   layout: sparse
#   node: idx[1*N] vals[1*N] zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N] ot[2*N*log(N)]
#   tags: none
#   other: none
#   note: built from N given values (index, value pairs) over any index range [lo, hi], every other index 0; costs are in N; wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left; OR by value: per level, a segment tree over its order (O(log N) a window); the structure is over the given values only, and the zeros of [l, r] are added in closed form (they sit between the negatives and the positives)

# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
# zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
from bisect import bisect_left, bisect_right
from itertools import accumulate


class WaveletMatrix:
    __slots__ = ('arr', 'n', 'srt', 'm', 'bits', 'zeros', 'zsum', 'ot')

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
        self.zsum = []
        self.ot = []  # per level, OR over its order
        for d in range(bits - 1, -1, -1):
            self.ot.append(self._orTab([srt[v] for v in cur]))
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            self.zsum.append(list(accumulate((0 if (v >> d) & 1 else srt[v] for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]
        self.ot.append(self._orTab([srt[v] for v in cur]))  # (the final order)

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]

    # O(logN) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self.countInValRange(l, r, x, x)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r, bisect_left(self.srt, lowVal))

    # O(logN) -- # of values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- # of values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- # of values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def countGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return r - l + 1 - self._countBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 0 <= l <= r < n and 1 <= k <= r - l + 1, else
    # IndexError
    def kthSmallest(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"kthSmallest: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMin(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMin: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- smallest value > x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def smallestGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"smallestGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == r - l + 1 else self._kth(l, r, c + 1)

    # O(logN) -- largest value <= x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_right(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- largest value < x in a[l..r], or None; needs 0 <= l <= r < n, else IndexError
    def largestLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"largestLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        c = self._countBelow(l, r, bisect_left(self.srt, x))
        return None if c == 0 else self._kth(l, r, c)

    # O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1)

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal; needs 0 <= l <= r < n, else IndexError
    def sumInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._sumBelow(l, r, bisect_right(self.srt, highVal)) - self._sumBelow(l, r, bisect_left(self.srt, lowVal))

    # O(logN) -- sum of the values < x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- sum of the values <= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- sum of the values > x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_right(self.srt, x))

    # O(logN) -- sum of the values >= x in a[l..r]; needs 0 <= l <= r < n, else IndexError
    def sumGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._sumFirst(l, r, r - l + 1) - self._sumBelow(l, r, bisect_left(self.srt, x))

    # O(logN) -- sum of the k smallest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else
    # IndexError
    def sumSmallestK(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumSmallestK: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(logN) -- sum of the k largest values in a[l..r]; needs 0 <= l <= r < n and 0 <= k <= r - l + 1, else
    # IndexError
    def sumLargestK(self, l, r, k):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumLargestK: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)

    # O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs 0 <= l <= r < n
    # and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumKthSmallestRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)

    # O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest);
    # needs 0 <= l <= r < n and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumKthLargestRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)

    # O(logN) -- sum of |a[i] - x| over i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def sumAbsDiffToX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"sumAbsDiffToX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        rk = bisect_left(self.srt, x)
        c, s = self._countBelow(l, r, rk), self._sumBelow(l, r, rk)
        return x * c - s + (self._sumFirst(l, r, r - l + 1) - s) - x * (r - l + 1 - c)

    # O(log^2 N) -- OR of the values < x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orLtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orLtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._orRanks(l, r, 0, bisect_left(self.srt, x))

    # O(log^2 N) -- OR of the values <= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orLteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orLteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._orRanks(l, r, 0, bisect_right(self.srt, x))

    # O(log^2 N) -- OR of the values > x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orGtX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orGtX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._orRanks(l, r, bisect_right(self.srt, x), self.m)

    # O(log^2 N) -- OR of the values >= x in a[l..r]; 0 if there are none; needs 0 <= l <= r < n, else IndexError
    def orGteX(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orGteX: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._orRanks(l, r, bisect_left(self.srt, x), self.m)

    # O(log^2 N) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none; needs
    # 0 <= l <= r < n, else IndexError
    def orInValRange(self, l, r, lowVal, highVal):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"orInValRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if lowVal > highVal:
            return 0
        return self._orRanks(l, r, bisect_left(self.srt, lowVal), bisect_right(self.srt, highVal))

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

    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1
    def _sumFirst(self, l, r, k):
        if k <= 0:
            return 0
        lo, hi, rank, res, d = l, r + 1, 0, 0, self.bits
        for z, zs in zip(self.zeros, self.zsum):
            d -= 1
            zl, zh = z[lo], z[hi]
            if k <= zh - zl:
                lo, hi = zl, zh
            else:  # all of this window's 0s are among the k smallest
                k -= zh - zl
                res += zs[hi] - zs[lo]
                rank |= 1 << d
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
        return res + k * self.srt[rank]  # the last k all equal the k-th smallest

    # sum of the a[i], i in [l, r], whose rank is < x
    def _sumBelow(self, l, r, x):
        if x <= 0:
            return 0
        if x >= self.m:
            return self._sumFirst(l, r, r - l + 1)
        lo, hi, res, d = l, r + 1, 0, self.bits
        for z, zs in zip(self.zeros, self.zsum):
            d -= 1
            zl, zh = z[lo], z[hi]
            if (x >> d) & 1:
                res += zs[hi] - zs[lo]
                lo, hi = z[-1] + lo - zl, z[-1] + hi - zh
            else:
                lo, hi = zl, zh
        return res

    @staticmethod
    def _orTab(vals):  # bottom-up segment tree: leaves at n..2n-1
        n = len(vals)
        t = [0] * n + vals
        for i in range(n - 1, 0, -1):
            t[i] = t[2 * i] | t[2 * i + 1]
        return t

    def _orQ(self, lv, lo, hi):  # OR of level lv's order at positions [lo, hi)
        t, res = self.ot[lv], 0
        lo += self.n
        hi += self.n
        while lo < hi:
            if lo & 1:
                res |= t[lo]
                lo += 1
            if hi & 1:
                hi -= 1
                res |= t[hi]
            lo >>= 1
            hi >>= 1
        return res

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

    # O(logN) -- a[i]; needs lo <= i <= hi, else IndexError
    def pointGet(self, i):
        if not self.lo <= i <= self.hi:
            raise IndexError(f"pointGet: needs lo <= i <= hi, got i = {i}")
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0

    # O(logN) -- # of i in [l, r] with a[i] == x; needs lo <= l <= r <= hi, else IndexError
    def countOccurrences(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countOccurrences: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countOccurrences(i0, i1, x) if i0 <= i1 else 0) + (zeros if x == 0 else 0)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal; needs lo <= l <= r <= hi, else IndexError
    def countInValRange(self, l, r, lowVal, highVal):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countInValRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        inside = self.inner.countInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0
        return inside + (zeros if lowVal <= 0 <= highVal else 0)

    # O(logN) -- # of values < x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countLtX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 < x else 0)

    # O(logN) -- # of values <= x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countLteX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 <= x else 0)

    # O(logN) -- # of values > x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countGtX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 > x else 0)

    # O(logN) -- # of values >= x in a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def countGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"countGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.countGteX(i0, i1, x) if i0 <= i1 else 0) + (zeros if 0 >= x else 0)

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs lo <= l <= r <= hi and 1 <= k <= r - l + 1,
    # else IndexError
    def kthSmallest(self, l, r, k):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"kthSmallest: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallest: needs 1 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._kth(l, r, k)

    # O(logN) -- min of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMin(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMin: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._kth(l, r, 1)

    # O(logN) -- max of a[l..r]; needs lo <= l <= r <= hi, else IndexError
    def rangeMax(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeMax: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        return self._kth(l, r, r - l + 1)

    # O(logN) -- smallest value >= x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def smallestGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"smallestGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        a = self.inner.smallestGteX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 >= x:
            a = 0 if a is None else min(a, 0)
        return a

    # O(logN) -- smallest value > x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def smallestGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"smallestGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        a = self.inner.smallestGtX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 > x:
            a = 0 if a is None else min(a, 0)
        return a

    # O(logN) -- largest value <= x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def largestLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"largestLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        a = self.inner.largestLteX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 <= x:
            a = 0 if a is None else max(a, 0)
        return a

    # O(logN) -- largest value < x in a[l..r], or None; needs lo <= l <= r <= hi, else IndexError
    def largestLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"largestLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        a = self.inner.largestLtX(i0, i1, x) if i0 <= i1 else None
        if zeros and 0 < x:
            a = 0 if a is None else max(a, 0)
        return a

    # O(logN) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else IndexError
    def rangeSum(self, l, r):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"rangeSum: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.rangeSum(i0, i1) if i0 <= i1 else 0

    # O(logN) -- sum of the a[i] in [l, r] with lowVal <= a[i] <= highVal (the zeros add nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def sumInValRange(self, l, r, lowVal, highVal):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumInValRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.sumInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0

    # O(logN) -- sum of the values < x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else IndexError
    def sumLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.sumLtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- sum of the values <= x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else IndexError
    def sumLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.sumLteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- sum of the values > x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else IndexError
    def sumGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.sumGtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- sum of the values >= x in a[l..r] (the zeros add nothing); needs lo <= l <= r <= hi, else IndexError
    def sumGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, _ = self._span(l, r)
        return self.inner.sumGteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- sum of the k smallest values in a[l..r]; needs lo <= l <= r <= hi and 0 <= k <= r - l + 1, else
    # IndexError
    def sumSmallestK(self, l, r, k):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumSmallestK: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if not 0 <= k <= r - l + 1:
            raise IndexError(f"sumSmallestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, k)

    # O(logN) -- sum of the k largest values in a[l..r]; needs lo <= l <= r <= hi and 0 <= k <= r - l + 1, else
    # IndexError
    def sumLargestK(self, l, r, k):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumLargestK: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        n = r - l + 1
        if not 0 <= k <= n:
            raise IndexError(f"sumLargestK: needs 0 <= k <= r - l + 1, got k = {k}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n) - self._sumFirst(l, r, n - k)

    # O(logN) -- sum of the kFrom-th..kTo-th smallest values of a[l..r] (1-indexed, inclusive); needs
    # lo <= l <= r <= hi and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthSmallestRange(self, l, r, kFrom, kTo):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumKthSmallestRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        if not 1 <= kFrom <= kTo <= r - l + 1:
            raise IndexError(f"sumKthSmallestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {r - l + 1}")
        return self._sumFirst(l, r, kTo) - self._sumFirst(l, r, kFrom - 1)

    # O(logN) -- sum of the kFrom-th..kTo-th largest values of a[l..r] (1-indexed, inclusive; (1, 3) = the 3 biggest);
    # needs lo <= l <= r <= hi and 1 <= kFrom <= kTo <= r - l + 1, else IndexError
    def sumKthLargestRange(self, l, r, kFrom, kTo):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumKthLargestRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        n = r - l + 1
        if not 1 <= kFrom <= kTo <= n:
            raise IndexError(f"sumKthLargestRange: needs 1 <= kFrom <= kTo <= r - l + 1, got "
                             f"kFrom = {kFrom}, kTo = {kTo}, r - l + 1 = {n}")
        return self._sumFirst(l, r, n - kFrom + 1) - self._sumFirst(l, r, n - kTo)

    # O(logN) -- sum of |a[i] - x| over i in [l, r]; needs lo <= l <= r <= hi, else IndexError
    def sumAbsDiffToX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"sumAbsDiffToX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return (self.inner.sumAbsDiffToX(i0, i1, x) if i0 <= i1 else 0) + zeros * abs(x)

    # O(logN) -- OR of the values < x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def orLtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"orLtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return self.inner.orLtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values <= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def orLteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"orLteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return self.inner.orLteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values > x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def orGtX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"orGtX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return self.inner.orGtX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the values >= x in a[l..r]; 0 if there are none (the zeros add nothing); needs
    # lo <= l <= r <= hi, else IndexError
    def orGteX(self, l, r, x):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"orGteX: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return self.inner.orGteX(i0, i1, x) if i0 <= i1 else 0

    # O(logN) -- OR of the a[i] with lowVal <= a[i] <= highVal in a[l..r]; 0 if there are none (the zeros add
    # nothing); needs lo <= l <= r <= hi, else IndexError
    def orInValRange(self, l, r, lowVal, highVal):
        if not self.lo <= l <= r <= self.hi:
            raise IndexError(f"orInValRange: needs lo <= l <= r <= hi, got l = {l}, r = {r}")
        i0, i1, zeros = self._span(l, r)
        return self.inner.orInValRange(i0, i1, lowVal, highVal) if i0 <= i1 else 0

    # the k-th smallest of a[l..r], 1 <= k <= r - l + 1
    def _kth(self, l, r, k):
        i0, i1, zeros = self._span(l, r)
        neg = self.inner.countLtX(i0, i1, 0) if i0 <= i1 else 0
        if k <= neg:
            return self.inner.kthSmallest(i0, i1, k)
        if k <= neg + zeros:
            return 0
        return self.inner.kthSmallest(i0, i1, k - zeros)

    # how many of the k smallest of [l, r] are given values (the rest are zeros), with i0, i1 from _span
    def _given(self, i0, i1, zeros, k):
        neg = self.inner.countLtX(i0, i1, 0) if i0 <= i1 else 0
        return k if k <= neg else max(neg, k - zeros)
    # sum of the k smallest of a[l..r], 0 <= k <= r - l + 1 (zeros add nothing)
    def _sumFirst(self, l, r, k):
        i0, i1, zeros = self._span(l, r)
        return self.inner.sumSmallestK(i0, i1, self._given(i0, i1, zeros, k)) if i0 <= i1 else 0
