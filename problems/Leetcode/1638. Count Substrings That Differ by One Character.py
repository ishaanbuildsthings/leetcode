class Solution:
    def countSubstrings(self, s: str, t: str) -> int:
        
        @cache
        def dp(i, j, misses):
            if i == len(s):
                return 0
            if j == len(t):
                return 0
            if s[i] != t[j]:
                misses += 1
            if misses == 2:
                return 0
            return misses + dp(i + 1, j + 1, misses)
        
        res = 0
        for i in range(len(s)):
            for j in range(len(t)):
                res += dp(i, j, 0)
        return res