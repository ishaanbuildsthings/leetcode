# https://leetcode.com/problems/maximum-difference-between-increasing-elements/
# difficulty: easy
# tags: prefix

# problem
# Given a 0-indexed integer array nums of size n, find the maximum difference between nums[i] and nums[j] (i.e., nums[j] - nums[i]), such that 0 <= i < j < n and nums[i] < nums[j].

# Return the maximum difference. If no such i and j exists, return -1.

# Solution, O(n) time O(1) space. Track smallest seen so far.

class Solution:
    def maximumDifference(self, nums: List[int]) -> int:
        res = -1
        smallest = float('inf')
        for i in range(len(nums)):
            smallest = min(smallest, nums[i])
            if nums[i] > smallest:
                res = max(res, nums[i] - smallest)
        return res
