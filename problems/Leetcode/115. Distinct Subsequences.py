class Solution:
    def numDistinct(self, s: str, t: str) -> int:
        @cache
        def dp(i, j):
            if j == len(t):
                return 1
            if i == len(s):
                return 0
            
            resThis = 0
            if s[i] == t[j]:
                resThis += dp(i + 1, j + 1)
            resThis += dp(i + 1, j)
            
            return resThis
    
        return dp(0, 0)