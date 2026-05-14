# https://leetcode.com/problems/minimum-operations-to-reduce-x-to-zero/description/?envType=daily-question&envId=2023-09-20
# Difficulty: Medium
# Tags: lop off

# Problem
# You are given an integer array nums and an integer x. In one operation, you can either remove the leftmost or the rightmost element from the array nums and subtract its value from x. Note that this modifies the array for future operations.

# Return the minimum number of operations to reduce x to exactly 0 if it is possible, otherwise, return -1.

# Solution, O(n) time and space
# This problem can be rephrased as find the largest subarray of sum equal to sum(nums) - x. We just maintain the earliest prefix for a cut off amount, then iterate through tracking a running sum.

class Solution:
    def minOperations(self, nums: List[int], x: int) -> int:
        target = sum(nums) - x # the sum we want our subarray to be
        longestSubbarayEqualTarget = float('-inf')
        earliestPrefix = {} # maps a sum to the earliest index it occurs at
        earliestPrefix[0] = -1 # we can always lop off a sum of 0

        runningSum = 0
        for i, num in enumerate(nums):
            runningSum += num
            if not runningSum in earliestPrefix:
                earliestPrefix[runningSum] = i
            amountNeededToCutOff = runningSum - target
            if amountNeededToCutOff in earliestPrefix:
                length = i - earliestPrefix[amountNeededToCutOff]
                longestSubbarayEqualTarget = max(longestSubbarayEqualTarget, length)


        if longestSubbarayEqualTarget == float('-inf'):
            return -1
        return len(nums) - longestSubbarayEqualTarget