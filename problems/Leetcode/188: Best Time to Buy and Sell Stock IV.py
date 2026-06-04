class Solution:
    def maxProfit(self, k: int, prices: List[int]) -> int:
        @cache
        def dp(i, completed, isHolding):
            return (
                0 if (i == len(prices) or completed == k) else 
                max(dp(i + 1, completed, isHolding), prices[i] + dp(i + 1, completed + 1, False)) if isHolding else 
                max(dp(i + 1, completed, isHolding), -prices[i] + dp(i + 1, completed, True)
            ))
            
        return dp(0, 0, False)