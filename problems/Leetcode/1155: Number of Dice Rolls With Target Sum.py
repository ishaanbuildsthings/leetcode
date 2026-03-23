class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        # O(n * target * k) time, O(n * target) space, top down dp
        # MOD = 10**9 + 7
        
        # @cache
        # def dp(diceLeft, sumLeft):
        #     # base case
        #     if diceLeft == 0:
        #         return sumLeft == 0
            
        #     resForThis = 0

        #     for diceRoll in range(1, k + 1):
        #         if sumLeft - diceRoll < 0:
        #             continue
        #         ifRollThat = dp(diceLeft - 1, sumLeft - diceRoll)
        #         resForThis += ifRollThat
            
        #     return resForThis % MOD
        
        # return dp(n, target)



        # O(n * target * k) time, O(target) space, bottom up dp
        # MOD = 10**9 + 7
        # dp = [0] * (target + 1)
        # dp[0] = 1
        # for i in range(n):
        #     ndp = [0] * (target + 1)
        #     for roll in range(1, k + 1):
        #         for oldTot in range(target + 1):
        #             ntot = oldTot + roll
        #             if ntot <= target:
        #                 ndp[ntot] += dp[oldTot]
        #                 ndp[ntot] %= MOD
        #     dp = ndp
        # return dp[-1]





        # O(n * k) time O(t) space bottom up prefix dp
        # MOD = 10**9 + 7
        
        # dp = [0] * (target + 1)
        # dp[0] = 1
        # for i in range(n):
        #     ndp = [0] * (target + 1)
        #     pf = []
        #     curr = 0
        #     for v in dp:
        #         curr += v
        #         curr %= MOD
        #         pf.append(curr)
        #     for newTot in range(1, target + 1):
        #         up = newTot - 1
        #         down = newTot - k
        #         ndp[newTot] += pf[up] - (pf[down - 1] if down - 1 >= 0 else 0)
        #         ndp[newTot] %= MOD
        #     dp = ndp
        # return dp[-1]
