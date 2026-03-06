class Solution:
    def rearrangeSticks(self, n: int, k: int) -> int:
        MOD = 10**9 + 7
        # go right to left, we either pick the tallest and it is visible, or we do not
        @cache
        def dp(sticksLeft, kLeft):
            if sticksLeft == 0:
                return int(kLeft == 0)
            
            ifPutBiggestOnRight = dp(sticksLeft - 1, kLeft - 1)
            otherStickOptions = sticksLeft - 1 # sticks that are not the tallest
            ifPutOtherOnRight = otherStickOptions * dp(sticksLeft - 1, kLeft)
            return (ifPutBiggestOnRight + ifPutOtherOnRight) % MOD
        
        ans = dp(n, k)
        dp.cache_clear()
        return ans