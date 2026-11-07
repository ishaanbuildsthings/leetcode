# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeMax/template.py
# @operations: maxAll pointGet rangeMax
# @data-structure-type: sparse-table
# @letters: same
# @complexities:
#   pointGet: 1
#   rangeMax: 1
#   maxAll: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sparse[1*N*log(N)]
#   tags: none
#   other: none
#   note: log(N) levels of N values each; level 0 is the array itself
# @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sparse-tables/SparseMax.py

# MAX sparse table
# O(n log n) build
# O(1) range MAX

class SparseMax:
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
                    val = max(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    # O(1) -- max of a[l..r]; needs 0 <= l <= r < n, else IndexError
    def rangeMax(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return max(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )

    # O(1) -- a[i]; needs needs 0 <= i < n, else IndexError, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")

    # O(1) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else raises IndexError
    def maxAll(self):
        if self.n < 1:
            raise IndexError("maxAll: needs n >= 1")
        return self.rangeMax(0, self.n - 1)
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.sparse[0][i]
