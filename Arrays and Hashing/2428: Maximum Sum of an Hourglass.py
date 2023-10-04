# https://leetcode.com/problems/maximum-sum-of-an-hourglass/description/
# difficulty: medium

# problem
# You are given an m x n integer matrix grid.

# We define an hourglass as a part of the matrix with the following form:

# Return the maximum sum of the elements of an hourglass.

# Note that an hourglass cannot be rotated and must be entirely contained within the matrix.

# Solution, O(n*m) time, O(1) space
# Just check every hourglass. I think my code was technically inefficient due to the slicing for arrays

class Solution:
    def maxSum(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        def getSum(r, c):
            return sum(grid[r][c:c+3]) + grid[r + 1][c + 1] + sum(grid[r + 2][c:c+3])

        res = 0
        for r in range(HEIGHT - 2):
            for c in range(WIDTH - 2):
                res = max(res, getSum(r, c))
        return res
