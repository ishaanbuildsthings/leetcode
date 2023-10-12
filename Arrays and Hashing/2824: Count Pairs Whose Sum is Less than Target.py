# https://leetcode.com/problems/count-pairs-whose-sum-is-less-than-target/description/
# difficulty: easy

# Problem
# Given a 0-indexed integer array nums of length n and an integer target, return the number of pairs (i, j) where 0 <= i < j < n and nums[i] + nums[j] < target.

# Solution, I just brute forced n^2 time, O(1) space
# We could sort and use two pointers for n log n.
# We could use a set and iterate values, but t's the same complexity as brute force due to the constraints.

class Solution:
    def countPairs(self, nums: List[int], target: int) -> int:
        res = 0
        for i in range(len(nums) - 1):
            for j in range(i + 1, len(nums)):
                if nums[i] + nums[j] < target:
                    res += 1
        return res