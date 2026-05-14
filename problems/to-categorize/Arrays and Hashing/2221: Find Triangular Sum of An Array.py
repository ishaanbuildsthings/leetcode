# https://leetcode.com/problems/find-triangular-sum-of-an-array/description/
# difficulty: medium
# tags: math, simulation

# Problem
# You are given a 0-indexed integer array nums, where nums[i] is a digit between 0 and 9 (inclusive).

# The triangular sum of nums is the value of the only element present in nums after the following process terminates:

# Let nums comprise of n elements. If n == 1, end the process. Otherwise, create a new 0-indexed integer array newNums of length n - 1.
# For each index i, where 0 <= i < n - 1, assign the value of newNums[i] as (nums[i] + nums[i+1]) % 10, where % denotes modulo operator.
# Replace the array nums with newNums.
# Repeat the entire process starting from step 1.
# Return the triangular sum of nums.

# Solution, O(n^2) time and O(n) space, just simulate it.
# I think an O(1) solution exists with math and mods. We can determine our contribution for each element.

class Solution:
    def triangularSum(self, nums: List[int]) -> int:
        # can be done in O(n) by computing how many times each value ends up in the final sum, and using mod math
        memo = [*nums]
        while len(memo) > 1:
            for i in range(len(memo) - 1):
                memo[i] = (memo[i] + memo[i + 1]) % 10
            memo.pop()
        return sum(memo)

