# https://leetcode.com/problems/sum-in-a-matrix/
# difficulty: medium

# Problem
# You are given a 0-indexed 2D integer array nums. Initially, your score is 0. Perform the following operations until the matrix becomes empty:

# From each row in the matrix, select the largest number and remove it. In the case of a tie, it does not matter which number is chosen.
# Identify the highest number amongst all those removed in step 1. Add that number to your score.
# Return the final score.

# Solution, sort each row then iterate over each cell, so O(rows * col log col) time, O(sort) space

class Solution:
    def matrixSum(self, nums: List[List[int]]) -> int:
        HEIGHT = len(nums)
        WIDTH = len(nums[0])

        for row in nums:
            row.sort(reverse=True)

        res = 0
        for c in range(WIDTH):
            runningMax = 0
            for r in range(HEIGHT):
                runningMax = max(runningMax, nums[r][c])
            res += runningMax

        return res
