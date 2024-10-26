# https://leetcode.com/problems/split-a-string-in-balanced-strings/
# difficulty: easy

# problem
# Balanced strings are those that have an equal quantity of 'L' and 'R' characters.

# Given a balanced string s, split it into some number of substrings such that:

# Each substring is balanced.
# Return the maximum number of balanced strings you can obtain.

# Solution, O(n) time and O(1) space

class Solution:
    def balancedStringSplit(self, s: str) -> int:
        res = 0
        lCount = 0
        rCount = 0
        for i in range(len(s)):
            if s[i] == 'L':
                lCount += 1
            else:
                rCount += 1
            if lCount == rCount:
                lCount, rCount = 0, 0
                res += 1
        return res