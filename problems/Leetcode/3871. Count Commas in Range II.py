class Solution:
    def countCommas(self, n: int) -> int:

        @cache
        def go(digits):
            if digits <= 3:
                return 0
            if digits <= 6:
                return 1
            if digits <= 9:
                return 2
            if digits <= 12:
                return 3
            if digits <= 15:
                return 4
            return 5

        s = str(n)
        @cache
        def dp(i, tight, zero, digits):
            if i == len(s):
                return go(digits)
            upper = 9 if not tight else int(s[i])
            resHere = 0
            for d in range(upper + 1):
                ntight = tight and d == upper
                nzero = zero and d == 0
                ndigits = digits + (0 if nzero else 1)
                resHere += dp(i + 1, ntight, nzero, ndigits)
            return resHere

        ans = dp(0,True,True,0)
        dp.cache_clear()
        return ans
                
            