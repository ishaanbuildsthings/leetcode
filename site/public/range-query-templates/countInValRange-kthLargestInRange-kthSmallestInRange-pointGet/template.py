# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/countInValRange-kthLargestInRange-kthSmallestInRange-pointGet/template.py
# @operations: countInValRange kthLargestInRange kthSmallestInRange pointGet
# @data-structure-type: wavelet
# @complexities:
#   countInValRange: log(N)
#   kthLargestInRange: log(N)
#   kthSmallestInRange: log(N)
#   pointGet: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: zeros[1*N*log(N)]
#   tags: none
#   other: arr[1*N] srt[1*N]
#   note: one row of N + 1 prefix counts per bit of the compressed value (wavelet matrix); no pointers, no per-node lists

# EXAMPLE
#   wm = WaveletMatrix(A)
#   v = wm.kthSmallestInRange(l, r, k)              # k = 1 is the min of A[l..r]
#   v = wm.kthLargestInRange(l, r, k)               # k = 1 is the max of A[l..r]
#   c = wm.countInValRange(l, r, lowVal, highVal)   # how many A[i] in [lowVal, highVal]
#
# Static array. Values are compressed to ranks 0..m-1, so costs are log of the number of distinct values, never log of
# the value range. Level d (top bit first) stably splits the current order into ranks with that bit 0, then bit 1;
# zeros[d][i] = # of the first i elements of level d's order with the bit 0. An index window [lo, hi) of level d maps
# to [zeros[d][lo], zeros[d][hi]) among the 0s and to [nz + lo - zeros[d][lo], ...) among the 1s (nz = all 0s).
# Indices 0-based, ranges inclusive. Everything is iterative.
from bisect import bisect_left, bisect_right
from itertools import accumulate


class WaveletMatrix:
    __slots__ = ("arr", "n", "srt", "m", "bits", "zeros")

    # O(N log N)
    def __init__(self, A):
        self.arr = A
        self.n = len(A)
        self.srt = srt = sorted(set(A))
        self.m = m = len(srt)
        self.bits = bits = max(1, (m - 1).bit_length())
        where = {v: k for k, v in enumerate(srt)}
        cur = [where[v] for v in A]
        self.zeros = []
        for d in range(bits - 1, -1, -1):
            self.zeros.append(list(accumulate((((v >> d) & 1) ^ 1 for v in cur), initial=0)))
            cur = [v for v in cur if not (v >> d) & 1] + [v for v in cur if (v >> d) & 1]

    # O(logN) -- the k-th smallest of a[l..r] (k = 1 is the min); needs 1 <= k <= r - l + 1, else IndexError
    def kthSmallestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthSmallestInRange: k = {k} is outside [1, {r - l + 1}]")
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

    # O(logN) -- the k-th largest of a[l..r] (k = 1 is the max); needs 1 <= k <= r - l + 1, else IndexError
    def kthLargestInRange(self, l, r, k):
        if not 1 <= k <= r - l + 1:
            raise IndexError(f"kthLargestInRange: k = {k} is outside [1, {r - l + 1}]")
        return self.kthSmallestInRange(l, r, r - l + 2 - k)

    # O(logN) -- # of i in [l, r] with lowVal <= a[i] <= highVal
    def countInValRange(self, l, r, lowVal, highVal):
        if lowVal > highVal:
            return 0
        return self._countBelow(l, r, bisect_right(self.srt, highVal)) - self._countBelow(l, r, bisect_left(self.srt, lowVal))

    # O(logN) -- # of i in [l, r] whose rank is < x
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

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.arr[i]
