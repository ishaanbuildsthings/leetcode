# https://leetcode.com/problems/make-array-zero-by-subtracting-equal-amounts/description/
# difficulty: easy

# Problem
# You are given a non-negative integer array nums. In one operation, you must:

# Choose a positive integer x such that x is less than or equal to the smallest non-zero element in nums.
# Subtract x from every positive element in nums.
# Return the minimum number of operations to make every element in nums equal to 0.

# Solution, O(n) time and space
class Solution:
    def minimumOperations(self, nums: List[int]) -> int:
        # as with many problems, can n log n time and O(1) space instead
        return len(set([num for num in nums if num]))