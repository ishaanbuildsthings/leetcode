class Solution:
    def maxProfit(self, prices: List[int]) -> int:
        cheapestBuy = float('inf')
        res = 0
        for price in prices:
            cheapestBuy = min(cheapestBuy, price)
            res = max(res, price - cheapestBuy)
        return res