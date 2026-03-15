# ⚠️ May be bad constant factor with function overhead?

class RangeSumQuery1d:
    def __init__(self, iterable):
        self.runningSum = 0
        self.prefixSums = []
        for num in iterable:
            self.runningSum += num
            self.prefixSums.append(self.runningSum)

    def sumQuery(self, l, r):
        if l == 0:
            return self.prefixSums[r]
        return self.prefixSums[r] - self.prefixSums[l - 1]

class Solution:
    def maxProfit(self, prices: List[int], strategy: List[int], k: int) -> int:
        pf = [] # how much we profit from ...i
        profit = 0
        for i in range(len(prices)):
            profit += strategy[i] * prices[i]
            pf.append(profit)

        sf = [0] * len(prices)
        profit = 0
        for i in range(len(prices) - 1, -1, -1):
            profit += strategy[i] * prices[i]
            sf[i] = profit

        res = -inf

        qq = RangeSumQuery1d(prices)

        for l in range(len(prices)):
            r = l + k - 1
            if r >= len(prices):
                break
            mr = l + (k//2)
            pricing = qq.sumQuery(mr, r)
            res = max(res, pricing + (sf[r + 1] if r + 1 < len(prices) else 0) + (pf[l-1] if l-1 >= 0 else 0))
        res = max(res, pf[-1])
        return res

        