class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        # O(26 * n^2)
        # @cache
        # def dp(l, r, outerChar):
        #     # base case
        #     if l >= r:
        #         return 0
            
        #     if s[l] == s[r] != outerChar:
        #         return 2 + dp(l + 1, r - 1, s[l])
            
        #     return max(
        #         dp(l + 1, r, outerChar),
        #         dp(l, r - 1, outerChar)
        #     )
        
        # return dp(0, len(s) - 1, 'G')


        # O(n^2)

        # returns (best1, best2, char1)
        @cache
        def dp(l, r):
            if l >= r:
                return (0, 0, '@')
            if s[l] != s[r]:
                opt1 = dp(l + 1, r)
                opt2 = dp(l, r - 1)
                if opt1[0] >= opt2[0]:
                    return [opt1[0], opt2[0], opt1[2]]
                return [opt2[0], opt1[0], opt2[2]]
            
            inner = dp(l + 1, r - 1)
            if s[l] != inner[2]:
                return [1 + inner[0], inner[0], s[l]]
            # if the chars do match we cannot use it
            return [inner[0], 1 + inner[1], inner[2]]
        
        ans = dp(0, len(s) - 1)
        return ans[0] * 2