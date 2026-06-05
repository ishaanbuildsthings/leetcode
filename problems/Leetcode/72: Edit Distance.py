# https://leetcode.com/problems/edit-distance/description/
# difficulty: medium
# tags: dynamic programming 2d, lcs

# Problem
# Given two strings word1 and word2, return the minimum number of operations required to convert word1 to word2.

# You have the following three operations permitted on a word:

# Insert a character
# Delete a character
# Replace a character

# Solution, O(n*m) time and space
# Standard LCS. Was a pretty cool realization that it works. Things like removing a character from one are equivalent to adding a character to the other!

class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        @cache
        def dp(i, j):
            # base case
            if i == len(word1):
                return len(word2) - j
            if j == len(word2):
                return len(word1) - i

            # if the letters are the same, we simply move on
            if word1[i] == word2[j]:
                return dp(i + 1, j + 1)

            resForThis = float('inf')

            ifDeleteFirst = 1 + dp(i + 1, j)
            ifDeleteSecond = 1 + dp(i, j + 1)
            ifReplaceFirst = 1 + dp(i + 1, j + 1)

            return min(ifDeleteFirst, ifDeleteSecond, ifReplaceFirst)
        return dp(0, 0)