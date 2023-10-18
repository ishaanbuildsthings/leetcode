# https://leetcode.com/problems/first-letter-to-appear-twice/description/
# difficulty: Easy

# Problem
# Given a string s consisting of lowercase English letters, return the first letter to appear twice.

# Note:

# A letter a appears twice before another letter b if the second occurrence of a is before the second occurrence of b.
# s will contain at least one letter that appears twice.


# Solution, O(min(# of lowercase letters, length of string)) time, O(lowercase letters) space

class Solution:
    def repeatedCharacter(self, s: str) -> str:
        charSet = set()
        for char in s:
            if char in charSet:
                return char
            charSet.add(char)
