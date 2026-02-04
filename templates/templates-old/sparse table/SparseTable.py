# # TEMPLATE BY ISHAAN AGRAWAL: https://github.com/ishaanbuildsthings
# # O(n log n) time to build, O(combineFn) time to query, so & is O(1) since AND-ing two numbers is constant

# class SparseTable:
#     def __init__(self, nums, combineFn):
#         BITS = math.ceil(math.log2(len(nums))) + 1

#         # Initialize the sparse table for all windows of length 1
#         sparse = [[None] * len(nums) for _ in range(BITS)] # sparse[log][left] is the answer to the fn operator for the subarray [left:left+2**power]
#         for left in range(len(nums)):
#             sparse[0][left] = nums[left]

#         for log in range(1, BITS):
#             for left in range(len(nums)):
#                 right = left + 2**log - 1
#                 if right >= len(nums):
#                     break
#                 leftHalfAnswer = sparse[log - 1][left]
#                 rightHalfAnswer = sparse[log - 1][int(left + (2**(log - 1)))]
#                 combinedAnswer = combineFn(leftHalfAnswer, rightHalfAnswer)
#                 sparse[log][left] = combinedAnswer

#         self.sparse = sparse
#         self.combineFn = combineFn

#     def query(self, l, r):
#         width = r - l + 1
#         power = math.floor(math.log2(width))
#         windowWidth = 2**power
#         leftAnswer = self.sparse[power][l]
#         rightSideStart = r - windowWidth + 1
#         rightAnswer = self.sparse[power][rightSideStart]
#         combinedAnswer = self.combineFn(leftAnswer, rightAnswer)
#         return combinedAnswer

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