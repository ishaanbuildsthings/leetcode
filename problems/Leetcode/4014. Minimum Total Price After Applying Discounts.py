class Solution:
    def minPrice(self, prices: list[int], discounts: list[int]) -> float:
        prices.sort(reverse=True)
        discounts.sort(reverse=True)
        res = 0
        for i in range(len(prices)):
            d = 0 if i >= len(discounts) else discounts[i]
            p = prices[i]
            np = (p * (100 - d)) / 100
            res += np
        return res3