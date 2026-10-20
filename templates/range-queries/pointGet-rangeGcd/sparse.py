# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeGcd/sparse.py
# @operations: pointGet rangeGcd
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: log(N)
#   rangeGcd: log(N)+log(U) ?
#   build: N*log(N)*log(U) ?
# @memory:
#   layout: sparse
#   node: sparse[2*N*log(N)]
#   tags: none
#   other: idx[1*N] vals[1*N] starts[2*N]
#   note: built from N (index, value) points over any index range [lo, hi], every other index 0; the sparse table runs on the points plus one 0 per gap (at most 2N + 1 elements)
# GCD sparse table
from math import gcd

class SparseGcd:
    def __init__(self, arr):
        self.n = len(arr)
        self.LOG = self.n.bit_length()
        self.sparse = [[0] * self.n for _ in range(self.LOG)]
        for i in range(self.n):
            self.sparse[0][i] = arr[i]
        for power in range(1, self.LOG):
            halfWidth = 1 << (power - 1)
            for left in range(self.n):
                val = self.sparse[power - 1][left]
                rightEdge = left + halfWidth
                if rightEdge < self.n:
                    val = gcd(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val
    # inclusive [l, r]
    def rangeGcd(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return gcd(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.sparse[0][i]

# ======================================================================================== sparse wrapper

from bisect import bisect_left, bisect_right


# Range gcd over any index range [lo, hi], built from (index, value) points; every other index is 0. A maximal gap
# of zeros adds nothing more than a single 0, so SparseGcd runs on the compressed array of points with one 0 per gap,
# and a query maps l and r to the compressed elements containing them.


class SparseStaticGcd:
    __slots__ = ("lo", "hi", "idx", "vals", "starts", "inner")

    # O(N log N) -- [lo, hi] all 0 except the given (index, value) points (distinct indices)
    def __init__(self, lo, hi, points):
        self.lo, self.hi = lo, hi
        pts = sorted(points)
        self.idx = [i for i, _ in pts]
        self.vals = [v for _, v in pts]
        starts, arr = [], []  # starts[k] = first index of compressed element k
        prev = lo - 1
        for i, v in pts:
            if i > prev + 1:
                starts.append(prev + 1)
                arr.append(0)
            starts.append(i)
            arr.append(v)
            prev = i
        if prev < hi:
            starts.append(prev + 1)
            arr.append(0)
        self.starts = starts
        self.inner = SparseGcd(arr)

    # O(logN) -- range gcd of a[l..r]
    def rangeGcd(self, l, r):
        return self.inner.rangeGcd(bisect_right(self.starts, l) - 1, bisect_right(self.starts, r) - 1)

    # O(logN) -- a[i]
    def pointGet(self, i):
        k = bisect_left(self.idx, i)
        return self.vals[k] if k < len(self.idx) and self.idx[k] == i else 0
