# https://leetcode.com/problems/first-unique-character-in-a-string/
# difficulty: easy

# Problem
# Given a string s, find the first non-repeating character in it and return its index. If it does not exist, return -1.

# Solution, O(n) time O(1) space

class Solution:
    def firstUniqChar(self, s: str) -> int:
        counts = Counter(s)
        for i, char in enumerate(s):
            if counts[char] == 1:
                return i
        return -1