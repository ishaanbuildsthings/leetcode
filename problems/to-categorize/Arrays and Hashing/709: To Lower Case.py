# https://leetcode.com/problems/to-lower-case/
# difficulty: easy

# Problem
# Given a string s, return the string after replacing every uppercase letter with the same lowercase letter.

# Solution, O(n) time and O(1) ? space, guessing under the hood its constructed in O(1) auxillary space but not sure

class Solution:
    def toLowerCase(self, s: str) -> str:
        return s.lower()