# https://leetcode.com/problems/maximum-profit-from-trading-stocks/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# You are given two 0-indexed integer arrays of the same length present and future where present[i] is the current price of the ith stock and future[i] is the price of the ith stock a year in the future. You may buy each stock at most once. You are also given an integer budget representing the amount of money you currently have.

# Return the maximum amount of profit you can make.

# Solution, standard dp
class Solution:
    def maximumProfit(self, present: List[int], future: List[int], budget: int) -> int:
        cache = [[None for _ in range(budget + 1)] for _ in range(len(present))]

        # @cache
        def dp(i, budgetLeft):
            if i == len(present):
                return 0

            if cache[i][budgetLeft] != None:
                return cache[i][budgetLeft]

            # if we skip this stock
            resThis = dp(i + 1, budgetLeft)

            # if we take this stock
            if present[i] <= budgetLeft:
                resThis = max(resThis, dp(i + 1, budgetLeft - present[i]) + future[i] - present[i])

            cache[i][budgetLeft] = resThis
            return resThis

        return dp(0, budget)