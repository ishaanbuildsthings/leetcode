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
    def query(self, l, r):
        width = r - l + 1
        maxPow = width.bit_length() - 1
        powWidth = 1 << maxPow
        return gcd(
            self.sparse[maxPow][l],
            self.sparse[maxPow][l + width - powWidth]
        )