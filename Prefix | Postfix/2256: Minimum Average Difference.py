# https://leetcode.com/problems/minimum-average-difference/
# difficulty: medium
# tags: prefix, postfix

# Problem
# You are given a 0-indexed integer array nums of length n.

# The average difference of the index i is the absolute difference between the average of the first i + 1 elements of nums and the average of the last n - i - 1 elements. Both averages should be rounded down to the nearest integer.

# Return the index with the minimum average difference. If there are multiple such indices, return the smallest one.

# Note:

# The absolute difference of two numbers is the absolute value of their difference.
# The average of n elements is the sum of the n elements divided (integer division) by n.
# The average of 0 elements is considered to be 0.

# Solution, standard prefix postfix, O(1) space is doable but I wrote an O(n) space one. O(n) time.

class Solution:
    def minimumAverageDifference(self, nums: List[int]) -> int:
        total = sum(nums)
        prefix = []
        runningSum = 0
        for i in range(len(nums)):
            runningSum += nums[i]
            prefix.append(runningSum)

        minimumDifference = float('inf')
        res = None

        for i in range(len(nums)):
            leftSum = prefix[i]
            rightSum = total - leftSum
            leftWidth = i + 1
            rightWidth = len(nums) - leftWidth
            leftAvg = math.floor(leftSum / leftWidth) if leftWidth else 0
            rightAvg = math.floor(rightSum / rightWidth) if rightWidth else 0
            diff = abs(leftAvg - rightAvg)
            if diff < minimumDifference:
                res = i
                minimumDifference = diff

        return res