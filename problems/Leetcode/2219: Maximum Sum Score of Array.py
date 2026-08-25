# https://leetcode.com/problems/maximum-sum-score-of-array/description/
# difficulty: medium

# Problem
# You are given a 0-indexed integer array nums of length n.

# The sum score of nums at an index i where 0 <= i < n is the maximum of:

# The sum of the first i + 1 elements of nums.
# The sum of the last n - i elements of nums.
# Return the maximum sum score of nums at any index.

# Solution, O(n) time O(1) space

class Solution:
    def maximumSumScore(self, nums: List[int]) -> int:
        tot = sum(nums)
        res = float('-inf')
        curr = 0
        for i in range(len(nums)):
            curr += nums[i]
            tot -= nums[i]
            res = max(res, curr, tot if i != len(nums) - 1 else float('-inf'))
        return res
