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
                    # key behavior here, we have to make sure we don't inadvertently allow two options that used the same letter
                    secondary = opt2[0] if opt2[2] != opt1[2] else max(opt1[1], opt2[1])
                    return [opt1[0], secondary, opt1[2]]
                secondary = opt1[0] if opt1[2] != opt2[2] else max(opt2[1], opt1[1])
                return [opt2[0], secondary, opt2[2]]
            
            inner = dp(l + 1, r - 1)
            if s[l] != inner[2]:
                return [1 + inner[0], inner[0], s[l]]
            # if the chars do match we cannot use it
            # this line might be able to be simplified a bit
            return [max(1 + inner[1], inner[0]), max(inner[0], inner[1]), s[l]]
        
        ans = dp(0, len(s) - 1)