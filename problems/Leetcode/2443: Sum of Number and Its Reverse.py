# https://leetcode.com/problems/sum-of-number-and-its-reverse/description/
# Difficulty: medium
# tags: math

# Problem
# Given a non-negative integer num, return true if num can be expressed as the sum of any non-negative integer and its reverse, or false otherwise.

# Solution
# O(n log number) time, O(log number) space
# For each number, do a log operation on that number to reverse it, see if they sum to the target

def reverseNum(num):
    reversedNum = 0
    while num:
        lastDigit = num % 10
        num //= 10
        reversedNum *= 10
        reversedNum += lastDigit
    return reversedNum

class Solution:
    def sumOfNumberAndReverse(self, num: int) -> bool:
        for n in range(num + 1):
            if n + reverseNum(n) == num: return True
        return False