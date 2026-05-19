# TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant
import math

class SparseTable:
    def __init__(self, nums, combineFn):
        n = len(nums)
        if n == 0:
            self.sparse = []
            self.combineFn = combineFn
            self.log2 = [0]
            return

        BITS = n.bit_length()

        sparse = [[0] * n for _ in range(BITS)]
        sparse[0] = nums[:]

        for log in range(1, BITS):
            half = 1 << (log - 1)
            length = 1 << log
            limit = n - length + 1
            rowPrev = sparse[log - 1]
            row = sparse[log]
            for left in range(limit):
                row[left] = combineFn(rowPrev[left], rowPrev[left + half])

        self.sparse = sparse
        self.combineFn = combineFn

        log2 = [0] * (n + 1)
        for i in range(2, n + 1):
            log2[i] = log2[i >> 1] + 1
        self.log2 = log2

    def query(self, l, r):
        width = r - l + 1
        power = self.log2[width]
        windowWidth = 1 << power
        leftAnswer = self.sparse[power][l]
        rightAnswer = self.sparse[power][r - windowWidth + 1]
        return self.combineFn(leftAnswer, rightAnswer)