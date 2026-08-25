class Solution:
    def longestPalindromicSubsequence(self, s: str, k: int) -> int:
        
        @cache
        def dist(a, b):
            return min( abs(ord(a)-ord(b)), 26-abs(ord(a)-ord(b)) )
            
            
        @cache
        def dp(l, r, opsLeft):
            if l == r:
                return 1
            if l > r:
                return 0
            if s[l] == s[r]:
                return 2 + dp(l + 1, r - 1, opsLeft)
            ifNoChange1 = dp(l + 1, r, opsLeft)
            ifNoChange2 = dp(l, r - 1, opsLeft)
            d = dist(s[l], s[r])
            # print(f' {s[l]}, {s[r]}')
            # print(f'dist: {d}')
            if opsLeft >= d:
                ifChange = 2 + dp(l + 1, r - 1, opsLeft - d)
                return max(ifChange, ifNoChange1, ifNoChange2)
            return max(ifNoChange1, ifNoChange2)
        
        a = dp(0, len(s) - 1, k)
        # print(f'a is: {a}')
        dp.cache_clear()
        return a