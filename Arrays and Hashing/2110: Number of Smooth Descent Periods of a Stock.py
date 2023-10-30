# https://leetcode.com/problems/number-of-smooth-descent-periods-of-a-stock/description/
# difficulty: medium
# tags: math

# Problem
# You are given an integer array prices representing the daily price history of a stock, where prices[i] is the stock price on the ith day.

# A smooth descent period of a stock consists of one or more contiguous days such that the price on each day is lower than the price on the preceding day by exactly 1. The first day of the period is exempted from this rule.

# Return the number of smooth descent periods.

# Solution, just iterate and use triangle numbers, O(n) time and O(1) space

class Solution:
    def getDescentPeriods(self, prices: List[int]) -> int:
        runningDescending = 0
        res = 0
        for i in range(len(prices)):
            price = prices[i]
            prev = prices[i-1] if i > 0 else float('inf')
            if price == prev - 1:
                runningDescending += 1
                res += runningDescending
            else:
                runningDescending = 1
                res += 1
        return res