# https://leetcode.com/problems/count-number-of-ways-to-place-houses/
# difficulty: medium
# tags: dynamic programming 1d

# Problem
# There is a street with n * 2 plots, where there are n plots on each side of the street. The plots on each side are numbered from 1 to n. On each plot, a house can be placed.

# Return the number of ways houses can be placed such that no two houses are adjacent to each other on the same side of the street. Since the answer may be very large, return it modulo 109 + 7.

# Note that if a house is placed on the ith plot on one side of the street, a house can also be placed on the ith plot on the other side of the street.

# Solution, O(n) time, O(n or 1) space depending on the solution, I've listed 3
MOD = 10**9 + 7
class Solution:
    def countHousePlacements(self, n: int) -> int:
        #2*n solution
        @cache
        def dp(i, prevTaken):
            # base
            if i == n:
                return 1
            resThis = 0
            if prevTaken:
                return dp(i + 1, False) % MOD
            return (dp(i + 1, False) + dp(i + 1, True)) % MOD

        return (dp(0, False) ** 2) % MOD


        # n solution
        # @cache
        # def dp(i):
        #     # base
        #     if i >= n:
        #         return 1

        #     return (dp(i + 1) + dp(i + 2)) % MOD

        # return (dp(0) ** 2) % MOD


        # space optimized
        # prevPlaced = 0
        # prevNotPlaced = 1
        # res = 1
        # for i in range(n):
        #     prevPlaced = prevNotPlaced
        #     prevNotPlaced = res
        #     res = prevPlaced + prevNotPlaced
        #     res %= MOD
        # return (res * res) % MOD
