MOD = 10**9 + 7

class Solution:
    def profitableSchemes(self, n: int, minProfit: int, group: List[int], profit: List[int]) -> int:
        @cache
        def dp(membersLeft, accruedProfit, i):
            # base case, nothing left to consider
            if i == len(group):
                return 1 if accruedProfit >= minProfit else 0
            
            resForThis = 0
            
            if membersLeft >= group[i]:
                newProfit = min(minProfit, accruedProfit + profit[i]) # reduce DP states, we don't need to track accrued profit anymore when it's >= minProfit
                ifTake = dp(membersLeft - group[i], newProfit, i + 1)
                resForThis += ifTake
            
            ifSkip = dp(membersLeft, accruedProfit, i + 1)
            resForThis += ifSkip

            return resForThis % MOD
        
        return dp(n, 0, 0)
            