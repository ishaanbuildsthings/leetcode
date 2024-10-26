# https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/
# difficulty: medium
# tags: dynamic programming 2d

# problem
# You have n dice, and each die has k faces numbered from 1 to k.

# Given three integers n, k, and target, return the number of possible ways (out of the kn total ways) to roll the dice, so the sum of the face-up numbers equals target. Since the answer may be too large, return it modulo 109 + 7.

# Solution, O(n*target*k) time, O(n*target) space
# just store the dice left and sum left, try all rolls

class Solution:
    def numRollsToTarget(self, n: int, k: int, target: int) -> int:
        MOD = 10**9 + 7

        @cache
        def dp(diceLeft, sumLeft):
            # base case
            if diceLeft == 0:
                return sumLeft == 0

            resForThis = 0

            for diceRoll in range(1, k + 1):
                if sumLeft - diceRoll < 0:
                    continue
                ifRollThat = dp(diceLeft - 1, sumLeft - diceRoll)
                resForThis += ifRollThat

            return resForThis % MOD

        return dp(n, target)