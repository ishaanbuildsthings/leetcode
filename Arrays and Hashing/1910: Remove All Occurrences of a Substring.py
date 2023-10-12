# https://leetcode.com/problems/remove-all-occurrences-of-a-substring/
# difficulty: medium

# Problem
# Given two strings s and part, perform the following operation on s until all occurrences of the substring part are removed:

# Find the leftmost occurrence of the substring part and remove it from s.
# Return s after removing all occurrences of part.

# A substring is a contiguous sequence of characters in a string.

# Solution, O(n^2) time, O(n) space
# Brute force was accepted so I just did that

class Solution:
    def removeOccurrences(self, s: str, part: str) -> str:
        while True:
            index = s.find(part)
            if index == -1:
                return s
            s = s[:index] + s[index + len(part):]

