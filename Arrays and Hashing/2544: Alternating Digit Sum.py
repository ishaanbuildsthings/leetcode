# https://leetcode.com/problems/alternating-digit-sum/
# Difficulty: easy

# Problem
# You are given a positive integer n. Each digit of n has a sign according to the following rules:

# The most significant digit is assigned a positive sign.
# Each other digit has an opposite sign to its adjacent digits.
# Return the sum of all digits with their corresponding sign.

# Solution, O(n) time and O(1) space
class Solution:
    def alternateDigitSum(self, n: int) -> int:
        evenIndexFromRightSum = 0
        oddIndexFromRightSum = 0
        parity = 0 # even
        length = 0
        while n:
            lastDigit = n % 10
            n //= 10
            if parity == 1:
                oddIndexFromRightSum += lastDigit
            else:
                evenIndexFromRightSum += lastDigit
            parity = 1 - parity
            length += 1
        if length % 2 == 0:
            return oddIndexFromRightSum - evenIndexFromRightSum
        return evenIndexFromRightSum - oddIndexFromRightSum

