class Solution:
    def isInterleave(self, s1: str, s2: str, s3: str) -> bool:
        if len(s1) + len(s2) != len(s3):
            return False
            
        @cache
        def dp(i, j, k):
            if k == len(s3):
                return True
            res = False
            if i < len(s1) and s1[i] == s3[k]:
                res = dp(i + 1, j, k + 1)
            if j < len(s2) and s2[j] == s3[k]:
                res = res or dp(i, j + 1, k + 1)
            return res
        
        return dp(0,0,0)