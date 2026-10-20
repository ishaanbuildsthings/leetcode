# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeAndQuery/template.py
# @operations: pointGet rangeAndQuery
# @data-structure-type: sparse-table
# @complexities:
#   pointGet: 1
#   rangeAndQuery: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sparse[1*N*log(N)]
#   tags: none
#   other: none
#   note: log(N) levels of N values each; level 0 is the array itself
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sparse-tables/SparseAND.py

# AND sparse table
# O(n log n) build
# O(1) range AND

class SparseAnd:
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
                    val &= self.sparse[power - 1][rightEdge]
                self.sparse[power][left] = val

    def rangeAndQuery(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return (
            self.sparse[maxPow][l] &
            self.sparse[maxPow][l + width - powWidth]
        )

    # O(1) -- a[i]
    def pointGet(self, i):
        return self.sparse[0][i]
