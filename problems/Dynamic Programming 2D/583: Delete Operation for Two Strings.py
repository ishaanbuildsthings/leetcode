# https://leetcode.com/problems/delete-operation-for-two-strings/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# Given two strings word1 and word2, return the minimum number of steps required to make word1 and word2 the same.

# In one step, you can delete exactly one character in either string.

# Solution O(n*m) time and space, standard lcs style dp
class Solution:
    def minDistance(self, word1: str, word2: str) -> int:
        @cache
        def dp(i, j):
            # base
            if i == len(word1):
                return len(word2) - j
            if j == len(word2):
                return len(word1) - i

            if word1[i] == word2[j]:
                return dp(i + 1, j + 1)

            return min(
                dp(i + 1, j),
                dp(i, j + 1),
            ) + 1

        return dp(0, 0)