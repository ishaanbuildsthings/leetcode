class Solution:
    def numWays(self, n: int, k: int) -> int:

        @cache
        def dp(i, lastConsecutive):
            # base case
            if i == n:
                return 1

            if lastConsecutive == 0:
                return k * dp(i + 1, 1)
            
            elif lastConsecutive == 1:
                return (k - 1) * dp(i + 1, 1) + dp(i + 1, 2)
            
            return (k - 1) * dp(i + 1, 1)
                
        return dp(0, 0)

