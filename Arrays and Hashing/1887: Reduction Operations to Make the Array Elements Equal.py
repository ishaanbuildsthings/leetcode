# https://leetcode.com/problems/reduction-operations-to-make-the-array-elements-equal/description/?envType=daily-question&envId=2023-11-19
# difficulty: medium

# problem
# Given an integer array nums, your goal is to make all elements in nums equal. To complete one operation, follow these steps:

# Find the largest value in nums. Let its index be i (0-indexed) and its value be largest. If there are multiple elements with the largest value, pick the smallest i.
# Find the next largest value in nums strictly smaller than largest. Let its value be nextLargest.
# Reduce nums[i] to nextLargest.
# Return the number of operations to make all elements in nums equal.

# Solution, we just sort and count, O(n log n) time, O(sort) space

class Solution:
    def reductionOperations(self, nums: List[int]) -> int:
        nums.sort()
        diffs = 0
        res = 0
        for i in range(1, len(nums)):
          if nums[i] != nums[i - 1]:
            diffs += 1
          res += diffs
        return res