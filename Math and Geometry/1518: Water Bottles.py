# https://leetcode.com/problems/water-bottles/description/
# difficulty: easy
# tags: math

# problem
# There are numBottles water bottles that are initially full of water. You can exchange numExchange empty water bottles from the market with one full water bottle.

# The operation of drinking a full water bottle turns it into an empty bottle.

# Given the two integers numBottles and numExchange, return the maximum number of water bottles you can drink.

# Solution, too lazy to derive time (seems log-like) but O(1) space, just simulate
class Solution:
    def numWaterBottles(self, numBottles: int, numExchange: int) -> int:
        res = 0
        full = numBottles
        empty = 0
        while full:
            empty += full
            res += full
            full = 0
            amountFullsWeGet = empty // numExchange
            amountEmptiesWeLose = amountFullsWeGet * numExchange
            empty -= amountEmptiesWeLose
            full += amountFullsWeGet
        return res