# https://leetcode.com/problems/maximum-matrix-sum/description/
# difficulty: medium

# Problem
# You are given an n x n integer matrix. You can do the following operation any number of times:

# Choose any two adjacent elements of matrix and multiply each of them by -1.
# Two elements are considered adjacent if and only if they share a border.

# Your goal is to maximize the summation of the matrix's elements. Return the maximum sum of the matrix's elements using the operation mentioned above.

# Solution, O(n^2) time and O(1) space, we can turn all negatives into positives if there are an even amount, otherwise we leave one negative which should be maximized

class Solution:
    def maxMatrixSum(self, matrix: List[List[int]]) -> int:
        HEIGHT = len(matrix)
        WIDTH = len(matrix[0])
        negatives = 0
        totalAllPositive = 0
        worstCaseNegative = float('inf')
        for r in range(HEIGHT):
            for c in range(WIDTH):
                negatives += matrix[r][c] < 0
                totalAllPositive += max(matrix[r][c], -1 * matrix[r][c])
                worstCaseNegative = min(worstCaseNegative, abs(matrix[r][c]))
        if negatives % 2 == 0:
            return totalAllPositive
        return totalAllPositive - (2 * worstCaseNegative)
