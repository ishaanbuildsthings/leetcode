class Solution:
    def almostPalindromic(self, s: str) -> int:

        @cache
        def dp(left, right):
            if left < 0 or right >= len(s):
                return 0
            if s[left] != s[right]:
                return 0
            if left == right:
                return 1
            return 2 + dp(left - 1, right + 1)
            
        res = 1
        for i in range(len(s)):
            j = i - 1
            k = i + 1
            used = False
            while j >= 0 and k < len(s):
                width = k - j + 1
                if s[j] == s[k]:
                    res = max(res, width)
                    j -= 1
                    k += 1
                else:
                    if used:
                        break
                    maxWidth = dp(j, k + 1)
                    width2 = dp(j - 1, k)
                    tot = width - 2 + max(maxWidth, width2)
                    res = max(res, tot)
                    break

        return res



    # a c bb a