# https://leetcode.com/problems/longer-contiguous-segments-of-ones-than-zeros/
# Difficulty: easy
# tags: sliding window variable

# Problem
# Given a binary string s, return true if the longest contiguous segment of 1's is strictly longer than the longest contiguous segment of 0's in s, or return false otherwise.

# For example, in s = "110100010" the longest continuous segment of 1s has length 2, and the longest continuous segment of 0s has length 3.
# Note that if there are no 0's, then the longest continuous segment of 0's is considered to have a length 0. The same applies if there is no 1's.

# Solution, O(n) time and O(1) space, just slide and check, I bet more efficient or cooler methods exist, also can add some pruning if we want to terminate early if not enough characters

class Solution:
    def checkZeroOnes(self, s: str) -> bool:
        longestZeroes = 0
        longestOnes = 0
        l = 0
        r = 0
        while r < len(s):
            while s[l] != s[r]:
                l += 1
            if s[r] == '1':
                longestOnes = max(longestOnes, r - l + 1)
            else:
                longestZeroes = max(longestZeroes, r - l + 1)
            r += 1
        return longestOnes > longestZeroes