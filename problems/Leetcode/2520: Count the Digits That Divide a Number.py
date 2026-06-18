# https://leetcode.com/problems/count-the-digits-that-divide-a-number/
# Difficulty: Easy
# Tags: Math

# Problem

# Given an integer num, return the number of digits in num that divide num.

# An integer val divides nums if nums % val == 0.

# Soltuion, O(log base 10) time, O(1) space
# Just check every digit.

class Solution:
    def countDigits(self, num: int) -> int:
        num2 = num
        res = 0
        while num2 > 0:
            lastDigit = num2 % 10
            num2 //= 10
            if num % lastDigit == 0:
                res += 1
        return res

