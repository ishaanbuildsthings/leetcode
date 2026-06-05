# https://leetcode.com/problems/profitable-schemes/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# There is a group of n members, and a list of various crimes they could commit. The ith crime generates a profit[i] and requires group[i] members to participate in it. If a member participates in one crime, that member can't participate in another crime.

# Let's call a profitable scheme any subset of these crimes that generates at least minProfit profit, and the total number of members participating in that subset of crimes is at most n.

# Return the number of schemes that can be chosen. Since the answer may be very large, return it modulo 109 + 7.

# Solution, O(members * minProfit * crimes)
# Clearly, we can iterate through each crime, taking it or not. We track the index we are at, accrued profit to know if we have a profitable scheme, and members left to know if we can take a crime. The issue is that the memory/time becomes too much. We need to cap accruedProfit to stay at `minProfit` once we reach that, to create state collisions. A really brilliant idea!

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
