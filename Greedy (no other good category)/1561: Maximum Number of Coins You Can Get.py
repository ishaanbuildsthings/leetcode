# https://leetcode.com/problems/maximum-number-of-coins-you-can-get/description/
# difficulty: medium
# tags: greedy

# problem
# There are 3n piles of coins of varying size, you and your friends will take piles of coins as follows:

# In each step, you will choose any 3 piles of coins (not necessarily consecutive).
# Of your choice, Alice will pick the pile with the maximum number of coins.
# You will pick the next pile with the maximum number of coins.
# Your friend Bob will pick the last pile.
# Repeat until there are no more piles of coins.
# Given an array of integers piles where piles[i] is the number of coins in the ith pile.

# Return the maximum number of coins that you can have.

# Solution, O(n log n) time, O(sort) space
# Alice can always get the biggest pile, so when she does, we should take the second biggest. We can sort and take the second biggest essentially, giving bob the lowest ones.

class Solution:
    def maxCoins(self, piles: List[int]) -> int:
        res = 0
        piles.sort(reverse=True)
        for i in range(0, int(len(piles) * 2 / 3), 2):
            res += piles[i + 1]
        return res

        # 9 8 7 6 5 4 3 2 1
        #   ^     ^     ^