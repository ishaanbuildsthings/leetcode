# https://leetcode.com/problems/find-numbers-with-even-number-of-digits/description/
# Difficulty: Easy
# tags: math

# Problem
# Given an array nums of integers, return how many of them contain an even number of digits.

# Solution, O(n log number) time, O(log number) space
# For each number, do a log operation on it to get the number of digits

class Solution:
    def findNumbers(self, nums: List[int]) -> int:
        res = 0
        for num in nums:
            digits = 0
            while num:
                num //= 10
                digits += 1
            if digits % 2 == 0:
                res += 1
        return res
