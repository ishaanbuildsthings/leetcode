class Solution:
    def getNumberOfBacklogOrders(self, orders: List[List[int]]) -> int:
        buys = [] # max heap
        sells = [] # min heap

        for price, amount, orderType in orders:
            if orderType == 1: # sell
                heapq.heappush(sells, (price, amount))
            elif orderType == 0: # buy
                heapq.heappush(buys, (-price, amount))
            while sells and buys and sells[0][0] <= -1 * buys[0][0]:
                sellPrice, sellAmount = heapq.heappop(sells)
                buyPrice, buyAmount = heapq.heappop(buys)
                buyPrice *= -1
                met = min(sellAmount, buyAmount)
                if sellAmount - met:
                    heapq.heappush(sells, (sellPrice, sellAmount - met))
                if buyAmount - met:
                    heapq.heappush(buys, (-1 * buyPrice, buyAmount - met))
        res = 0
        for _, amt in buys:
            res += amt
        for _, amt in sells:
            res += amt
        return res % (10**9 + 7)


