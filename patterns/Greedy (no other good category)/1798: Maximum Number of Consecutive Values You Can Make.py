# https://leetcode.com/problems/maximum-number-of-consecutive-values-you-can-make/description/
# difficulty: medium
# tags: greedy

# Problem
# You are given an integer array coins of length n which represents the n coins that you own. The value of the ith coin is coins[i]. You can make some value x if you can choose some of your n coins such that their values sum up to x.

# Return the maximum number of consecutive integer values that you can make with your coins starting from and including 0.

# Note that you may have multiple coins of the same value.

# Solution, O(sort)

class Solution:
    def getMaximumConsecutive(self, coins: List[int]) -> int:
        coins.sort()
        tot = 0
        for i in range(len(coins)):
            if coins[i] - 1 <= tot:
                tot += coins[i]
            else:
                break
        return tot + 1
