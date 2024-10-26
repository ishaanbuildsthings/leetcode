# https://leetcode.com/problems/percentage-of-letter-in-string/description/
# difficulty: easy
# tags: math

# Problem
# Given a string s and a character letter, return the percentage of characters in s that equal letter rounded down to the nearest whole percent.

# Solution, O(n) time and O(1) space

class Solution:
    def percentageLetter(self, s: str, letter: str) -> int:
        occurences = 0
        for char in s:
            if char == letter:
                occurences += 1
        return math.floor(occurences / len(s) * 100)