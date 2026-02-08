# MIN sparse table
# O(n log n) build
# O(1) range MIN

class SparseMin:
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
                    val = min(val, self.sparse[power - 1][rightEdge])
                self.sparse[power][left] = val

    def query(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return min(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )
