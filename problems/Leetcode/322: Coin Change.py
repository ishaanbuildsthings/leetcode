class Solution:
    def coinChange(self, coins: List[int], amount: int) -> int:
        # unbound knapsack, cache[amt] depends on a smaller amt, so we loop up
        # order of loops does not matter as long as we loop UP

        # cache = [inf] * (amount + 1)
        # cache[0] = 0
        # for coin in coins:
        #     for amt in range(coin, amount + 1):
        #         cache[amt] = min(cache[amt], cache[amt - coin] + 1)
        # return cache[-1] if cache[-1] != inf else -1

        cache = [inf] * (amount + 1)
        cache[0] = 0
        for amt in range(1, amount + 1):
            for coin in coins:
                if amt - coin < 0:
                    continue
                cache[amt] = min(cache[amt], cache[amt - coin] + 1)
        return cache[-1] if cache[-1] != inf else -1

        # DUPLICATING OUR CACHE CANNOT SAVE US FROM SWITCHING THE ORDER THE LOOP ITERATES IN
        # we can go down, by reformulating what dp[x] means, but it is the same question
        
