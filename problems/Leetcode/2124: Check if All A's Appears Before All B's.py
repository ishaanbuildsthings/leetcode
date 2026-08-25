# https://leetcode.com/problems/check-if-all-as-appears-before-all-bs/
# difficulty: easy

# Problem
# Given a string s consisting of only the characters 'a' and 'b', return true if every 'a' appears before every 'b' in the string. Otherwise, return false.

# Solution, O(n) time and O(1) space, check if an A comes after a B
class Solution:
    def checkString(self, s: str) -> bool:
        seenB = False
        for char in s:
            seenB = seenB or char == 'b'
            if char == 'a' and seenB:
                return False
        return True