class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        @cache
        def dp(i, j):
            # base case, if we fully run out of one string, the LCS is 0
            if i == len(text1) or j == len(text2):
                return 0
            
            # if there's a match, just increment both
            if text1[i] == text2[j]:
                return 1 + dp(i + 1, j + 1)
            
            # otherwise, try incrementing one or the other
            return max(dp(i + 1, j), dp(i, j + 1))
        
        return dp(0, 0)