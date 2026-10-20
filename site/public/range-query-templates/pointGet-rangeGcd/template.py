# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeGcd/template.py
# @operations: pointGet rangeGcd
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: 1
#   rangeGcd: log(U) ?
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
    # O(logU) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0)
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