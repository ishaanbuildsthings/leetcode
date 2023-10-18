# https://leetcode.com/problems/average-value-of-even-numbers-that-are-divisible-by-three/
# Difficulty: Easy
# tags: arrays, math

# Problem
# Given an integer array nums of positive integers, return the average value of all even integers that are divisible by 3.

# Note that the average of n elements is the sum of the n elements divided by n and rounded down to the nearest integer.

# Solution, O(n) time and O(1) space
# Iterate, check each element

class Solution:
    def averageValue(self, nums: List[int]) -> int:
        count = 0
        total = 0
        for num in nums:
            if num % 6 == 0:
                count += 1
                total += num
        return total // count if count else 0