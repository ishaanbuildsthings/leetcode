# https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram/
# difficulty: medium

# Problem
# You are given two strings of the same length s and t. In one step you can choose any character of t and replace it with another character.

# Return the minimum number of steps to make t an anagram of s.

# An Anagram of a string is a string that contains the same characters with a different (or the same) ordering.

# Solution, O(n) time and O(1) space, count characters and use differences in the counts

ABC = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def minSteps(self, s: str, t: str) -> int:
        c1 = collections.Counter(s)
        c2 = collections.Counter(t)
        diffs = 0
        for char in ABC:
        # more efficient if we grab the length of one we can compute diffs without iterating over every letter
            diffs += abs(c1[char] - c2[char])
        return int(diffs / 2)