# https://leetcode.com/problems/minimum-number-of-steps-to-make-two-strings-anagram-ii/description/
# difficulty: medium

# Problem


# You are given two strings s and t. In one step, you can append any character to either s or t.

# Return the minimum number of steps to make s and t anagrams of each other.

# An anagram of a string is a string that contains the same characters with a different (or the same) ordering.

# Solution
# Just add the differences in letters, O(n+m) time, O(26) space

ABC = 'abcdefghijklmnopqrstuvwxyz'

class Solution:
    def minSteps(self, s: str, t: str) -> int:
        counts1 = Counter(s)
        counts2 = Counter(t)

        return sum(
            abs(counts1[char] - counts2[char])
            for char in ABC
        )