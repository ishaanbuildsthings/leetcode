# https://leetcode.com/problems/left-and-right-sum-differences/
# Difficulty: Easy
# Tags: prefix, postfix

# Problem
# Given a 0-indexed integer array nums, find a 0-indexed integer array answer where:

# answer.length == nums.length.
# answer[i] = |leftSum[i] - rightSum[i]|.
# Where:

# leftSum[i] is the sum of elements to the left of the index i in the array nums. If there is no such element, leftSum[i] = 0.
# rightSum[i] is the sum of elements to the right of the index i in the array nums. If there is no such element, rightSum[i] = 0.
# Return the array answer.

# Solution, O(n) time and O(1) space. Instead of generating the prefixes and postfixes we can do O(1) space and just slide.

class Solution:
    def leftRightDifference(self, nums: List[int]) -> List[int]:
        rightSum = sum(nums)
        leftSum = 0
        res = []
        for i in range(len(nums)):
            rightSum -= nums[i]
            if i > 0:
                leftSum += nums[i - 1]
            res.append(abs(leftSum - rightSum))
        return res
