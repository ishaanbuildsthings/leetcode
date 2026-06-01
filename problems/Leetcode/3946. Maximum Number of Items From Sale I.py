# items =
# [[1,1],[1,2]]
# budget =
# 3
# Use Testcase
# Output
# 3
# Expected
# 4


class Solution:
    def maximumSaleItems(self, items: List[List[int]], budget: int) -> int:

        # [[1,1],[1,2]]
        # budget = 3

        # numToFree = defaultdict(int)



        allNums = set()
        for fac, price in items:
            allNums.add(fac)

        MX = max(allNums)
        # print(f'{MX=}')

        numToFree = [0] * (MX + 1)

        c = [0] * (MX + 1)

        # c = Counter()
        for fac, price in items:
            c[fac] += 1

        for fac in allNums:
            for mult in range(fac, MX + 1, fac):
                if mult == fac:
                    numToFree[fac] += c[mult] - 1
                else:
                    numToFree[fac] += c[mult]
                    

        # print(f'num to free: {numToFree=}')

        n = len(items)
        # memo = [[-1] * 2 for _ in range(budget + 1) for _ in range(n + 1)]
        memo = [[[-1] * 2 for _ in range(budget + 1)] for _ in range(n + 1)]

        # @cache
        
        def dp(i, b, freeUsed):
            if i == len(items):
                return 0
            if memo[i][b][freeUsed] != -1:
                return memo[i][b][freeUsed]
            res = 0
            ifSkip = dp(i + 1, b, 0)
            fac, price = items[i]
            if price > b:
                memo[i][b][freeUsed] = ifSkip
                return ifSkip
            copiesGainedIfBought = (1 + numToFree[fac]) if not freeUsed else 1
            ifBuy = copiesGainedIfBought + dp(i, b - price, 1)

            memo[i][b][freeUsed] = max(ifSkip, ifBuy, 0)
            return memo[i][b][freeUsed]

        ans = dp(0, budget, 0)
        # dp.cache_clear()
        return ans