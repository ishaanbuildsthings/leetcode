# https://leetcode.com/problems/remove-trailing-zeros-from-a-string/
# Difficulty: Easy

# Problem
# Given a positive integer num represented as a string, return the integer num without trailing zeros as a string.

# Solution, O(n) time O(1) space

class Solution:
    def removeTrailingZeros(self, num: str) -> str:
        lastPointer = len(num) - 1
        while lastPointer > 0: # no leading 0s
            if num[lastPointer] == '0':
                lastPointer -= 1
            else:
                break
        return num[:lastPointer + 1]