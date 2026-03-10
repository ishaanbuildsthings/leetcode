class Solution:
    def numberOfStableArrays(self, zero: int, one: int, limit: int) -> int:
        # bottom up prefix dp
        # dp[z][o][lastBit] is the # of ways to make an array with z zeroes, o ones, and the lastBit was that number (we will place the opposite number now)

        MOD = 10**9 + 7
        dp = [[[0 for _ in range(2)] for _ in range(one + 1)] for _ in range(zero + 1)]
        dp[0][0][0] = 1
        dp[0][0][1] = 1


        # we need sum of dp[l...r][X][1]
        # and            dp[X][l...r][0]

        pref1 = [[0 for _ in range(one + 1)] for _ in range(zero + 1)] # pref1[l...r][X] like this
        pref0 = [[0 for _ in range(one + 1)] for _ in range(zero + 1)] # pref0[X][l...r] like this
        
        for newTotZero in range(zero + 1):
            for newTotOne in range(one + 1):
                if newTotZero:
                    lo = pref1[newTotZero - 1 - limit][newTotOne] if newTotZero - 1 - limit >= 0 else 0
                    hi = pref1[newTotZero - 1][newTotOne]
                    # placing zeroes
                    dp[newTotZero][newTotOne][0] = (hi - lo) % MOD
                # for placeZeroes in range(1, min(limit, newTotZero) + 1):
                #     dp[newTotZero][newTotOne][0] += dp[newTotZero-placeZeroes][newTotOne][1]
                #     dp[newTotZero][newTotOne][0] %= MOD
                
                # placing ones
                if newTotOne:
                    hi = pref0[newTotZero][newTotOne - 1]
                    lo = pref0[newTotZero][newTotOne - 1 - limit] if newTotOne - 1 - limit >= 0 else 0
                    dp[newTotZero][newTotOne][1] = (hi - lo) % MOD
                # for placeOnes in range(1, min(limit, newTotOne) + 1):
                #     dp[newTotZero][newTotOne][1] += dp[newTotZero][newTotOne-placeOnes][0]
                #     dp[newTotZero][newTotOne][1] %= MOD

                pref1[newTotZero][newTotOne] = ((pref1[newTotZero - 1][newTotOne] if newTotZero > 0 else 0) + dp[newTotZero][newTotOne][1]) % MOD
                pref0[newTotZero][newTotOne] = ((pref0[newTotZero][newTotOne - 1] if newTotOne > 0 else 0) + dp[newTotZero][newTotOne][0]) % MOD
        
        ans = (dp[zero][one][0] + dp[zero][one][1]) % MOD
        return ans

        


        # MOD = 10**9 + 7

        # UNSET = -1
        # ss_cache = [[[UNSET] * 2 for _ in range(one + 2)] for _ in range(zero + 2)]
        # dp_cache = [[[UNSET] * 2 for _ in range(one + 2)] for _ in range(zero + 2)]

        # def suffixSum(zeroesUsed, onesUsed, turn):
        #     if turn == 0:
        #         if onesUsed > one:
        #             return 0
        #     elif turn == 1:
        #         if zeroesUsed > zero:
        #             return 0

        #     if ss_cache[zeroesUsed][onesUsed][turn] != UNSET:
        #         return ss_cache[zeroesUsed][onesUsed][turn]

        #     nz = zeroesUsed + 1 if turn else zeroesUsed
        #     no = onesUsed if turn else onesUsed + 1
        #     res = (dp(zeroesUsed, onesUsed, turn) + suffixSum(nz, no, turn)) % MOD
        #     ss_cache[zeroesUsed][onesUsed][turn] = res
        #     return res

        # def dp(zeroesUsed, onesUsed, turnToPlace):
        #     index = zeroesUsed + onesUsed

        #     if index == zero + one:
        #         return int(zeroesUsed == zero and onesUsed == one)
        #     if index > zero + one:
        #         return 0

        #     if dp_cache[zeroesUsed][onesUsed][turnToPlace] != UNSET:
        #         return dp_cache[zeroesUsed][onesUsed][turnToPlace]

        #     maxPlaced = limit
        #     res = 0

        #     if turnToPlace == 0:
        #         lo = zeroesUsed + 1
        #         hi = zeroesUsed + maxPlaced
        #         res += suffixSum(lo, onesUsed, turnToPlace ^ 1) - suffixSum(hi + 1, onesUsed, turnToPlace ^ 1)
        #     else:
        #         lo = onesUsed + 1
        #         hi = onesUsed + maxPlaced
        #         res += suffixSum(zeroesUsed, lo, turnToPlace ^ 1) - suffixSum(zeroesUsed, hi + 1, turnToPlace ^ 1)

        #     res %= MOD
        #     dp_cache[zeroesUsed][onesUsed][turnToPlace] = res
        #     return res

        # a = (dp(0, 0, 1) + dp(0, 0, 0)) % MOD
        # ss_cache = []
        # dp_cache = []
        # return a