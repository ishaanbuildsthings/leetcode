# https://leetcode.com/problems/palindrome-partitioning-ii/description/
# Difficulty: Hard
# Tags: Dynamic Programming 2d, palindrome

# Problem
# Given a string s, partition s such that every substring of the partition is a palindrome.

# Return the minimum cuts needed for a palindrome partitioning of s.

# Solution, O(n^2) time and space
# For each string [i:], consider up to n splits (only if the left region is a palindrome). We preprocess all palindromes in n^2 time.

class Solution:
    def minCut(self, s: str) -> int:
        # isPal[l][r] tells us if [l:r] is a palindrome
        isPal = [[False for _ in s] for _ in s]
        # 1 letter pals
        for i in range(len(s)):
            isPal[i][i] = True
        # 2 letter pals
        for l in range(len(s) - 1):
            if s[l] == s[l+1]:
                isPal[l][l+1] = True
        # length 3 or more pals
        for size in range(3, len(s) + 1):
            for l in range(len(s) - size + 1):
                r = l + size - 1
                if s[l] == s[r] and isPal[l+1][r-1]:
                    isPal[l][r] = True

        @cache
        def dp(i):
            # base case
            if isPal[i][len(s) - 1]:
                return 0

            resForThis = float('inf')

            for splitBefore in range(i + 1, len(s)):
                if isPal[i][splitBefore - 1]:
                    ifSplitHere = 1 + dp(splitBefore)
                    resForThis = min(resForThis, ifSplitHere)

            return resForThis

        return dp(0)
