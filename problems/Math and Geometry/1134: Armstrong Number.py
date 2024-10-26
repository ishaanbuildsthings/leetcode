# https://leetcode.com/problems/armstrong-number/description/
# difficulty: easy
# tags: math

# Problem
# Given an integer n, return true if and only if it is an Armstrong number.

# The k-digit number n is an Armstrong number if and only if the kth power of each digit sums to n.

# Solution, O(log n or 1) time, O(1) space, get each digit and add them, first get the length

class Solution:
    def isArmstrong(self, n: int) -> bool:
        num = n

        length = 0
        while num:
            length += 1
            num //= 10

        total = 0

        num = n
        while num:
            lastDigit = num % 10
            total += (lastDigit**length)
            num //= 10

        return total == n