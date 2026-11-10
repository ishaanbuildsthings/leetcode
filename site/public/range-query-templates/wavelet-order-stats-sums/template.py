# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/wavelet-order-stats-sums/template.py
# @operations: countGtX countGteX countInValRange countLtX countLteX countOccurrences kthSmallest largestLtX largestLteX maxAll minAll pointGet rangeMax rangeMin rangeSum smallestGtX smallestGteX sumAbsDiffToX sumAll sumGtX sumGteX sumInValRange sumKthLargestRange sumKthSmallestRange sumLargestK sumLtX sumLteX sumSmallestK
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
#   pointGet: 1
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
#   sumAll: log(N)
#   minAll: log(N)
#   maxAll: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: zeros[1*N*log(N)] zsum[1*N*log(N)] arr[1*N] srt[1*N]
#   tags: none
#   other: none
#   note: wavelet matrix: one row of N + 1 prefix counts per bit of the compressed value, plus one row of prefix sums of the values that go left

# Static array. Each query treats a[l..r] (0-indexed, inclusive) as a sorted multiset. Values are compressed to ranks
# 0..m-1 once, so costs are log of the number of distinct values, never of the value range; query arguments (x, lowVal,
# ...) can be anything. Level d of the wavelet matrix (top bit first) stably splits the current order into the ranks
# with that bit 0, then 1; zeros[d][i] = # of the first i elements of level d's order with the bit 0, so a window
# [lo, hi) maps to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s.
# zsum[d][i] = sum of the values among the first i elements of level d's order whose bit is 0.
from bisect import bisect_left, bisect_right
from itertools import accumulate, compress
from operator import ne


class WaveletMatrix:
    __slots__ = ('arr', 'n', 'srt', 'm', 'bits', 'zeros', 'zsum')

    # O(N log N) -- arr: the initial array (a list), 0-indexed
    def __init__(self, arr):
        self.arr = arr
        self.n = len(arr)
        order = sorted(range(self.n), key=arr.__getitem__)  # ranks by sorting, so no value is ever hashed
        s = [arr[i] for i in order]
        up = list(map(ne, s, s[1:]))  # up[k]: s[k + 1] starts a new distinct value
        self.srt = srt = s[:1] + list(compress(s[1:], up))
        self.m = m = len(srt)
        self.bits = bits = max(1, (m - 1).bit_length())
        cur = [0] * self.n
        for i, k in zip(order, accumulate(up, initial=0)):
            cur[i] = k
        self.zeros = []
        self.zsum = []
        for d in range(bits - 1, -1, -1):
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            self.zsum.append(list(accumulate((0 if (v >> d) & 1 else srt[v] for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]

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
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r,
            bisect_left(self.srt, lowVal))

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
        return self._sumBelow(l, r, bisect_right(self.srt, highVal)) - self._sumBelow(l, r,
            bisect_left(self.srt, lowVal))

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

    # O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else raises IndexError
    def minAll(self):
        if self.n < 1:
            raise IndexError("minAll: needs n >= 1")
        return self.rangeMin(0, self.n - 1)

    # O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)

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
