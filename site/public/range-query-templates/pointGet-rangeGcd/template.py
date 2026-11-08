# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointGet-rangeGcd/template.py
# @operations: gcdAll pointGet rangeGcd
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: 1
#   rangeGcd: log(U) ?
#   gcdAll: log(U) ?
#   build: N*log(N)*log(U) ?
# @memory:
#   layout: none
#   node: sparse[1*N*log(N)]
#   tags: none
#   other: none
#   note: log(N) levels of N values each; level 0 is the array itself
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sparse-tables/SparseGCD.py

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
    # O(logU) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0); needs 0 <= l <= r < n, else IndexError
    def rangeGcd(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeGcd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return gcd(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.sparse[0][i]

    # O(log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else raises IndexError
    def gcdAll(self):
        if self.n < 1:
            raise IndexError("gcdAll: needs n >= 1")
        return self.rangeGcd(0, self.n - 1)