class Solution:
    def maximumProfit(self, prices: List[int], k: int) -> int:

        @cache
        def dp(i, isBuyOpen, isShortOpen, txCompleted):
            if txCompleted > k:
                return -inf
            if i == len(prices):
                return 0 if not isShortOpen else -inf
            ifSkip = dp(i + 1, isBuyOpen, isShortOpen, txCompleted)

            res = ifSkip

            if isBuyOpen:
                ifSell = prices[i] + dp(i + 1, False, False, txCompleted + 1)
                res = max(res, ifSell)

            if not isBuyOpen and not isShortOpen:
                ifBuy = -prices[i] + dp(i + 1, True, False, txCompleted)
                ifOpenShort = prices[i] + dp(i + 1, False, True, txCompleted)
                res = max(res, ifBuy, ifOpenShort)

            if isShortOpen:
                ifCloseShort = -prices[i] + dp(i + 1, False, False, txCompleted + 1)
                res = max(res, ifCloseShort)

            return res

        a = dp(0,False,False,0)
        dp.cache_clear()
        return a