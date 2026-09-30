class Solution:
    def maxProfit(self, prices: List[int], cooldown: int, costs: List[int]) -> int:
        n = len(prices)
        
        @cache
        def dp(i):
            if i >= n:
                return 0
            # if skip
            res = dp(i + 1)
            # hold from i...j
            for j in range(i, n):
                pay = prices[i]
                sell = prices[j]
                profit = sell - pay
                fee = costs[j - i]
                totalProfit = profit - fee + dp(j + 1 + cooldown)
                res = max(res, totalProfit)
            return res
        
        return dp(0)
