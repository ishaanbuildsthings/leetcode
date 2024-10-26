# https://leetcode.com/problems/dice-roll-simulation/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# A die simulator generates a random number from 1 to 6 for each roll. You introduced a constraint to the generator such that it cannot roll the number i more than rollMax[i] (1-indexed) consecutive times.

# Given an array of integers rollMax and an integer n, return the number of distinct sequences that can be obtained with exact n rolls. Since the answer may be too large, return it modulo 109 + 7.

# Two sequences are considered different if at least one element differs from each other.

# Solution, O(n * consecutive rolls (max can be 15) * last roll (max can be 6) * 6) time, O(n * consecutive rolls * last roll) space
# Instead of uniquely tracking the amount of rolls in a row for each roll type, just track the last roll and the consecutive number of those rolls.

MOD = 10**9 + 7
class Solution:
    def dieSimulator(self, n: int, rollMax: List[int]) -> int:
        @cache
        def dp(rollsLeft, consecutiveNumbers, lastRoll):
            # base case
            if rollsLeft == 0:
                return 1

            resForThis = 0
            for newRoll in range(1, 7):
                if newRoll != lastRoll:
                    ifRollThis = dp(rollsLeft - 1, 1, newRoll)
                    resForThis += ifRollThis
                else:
                    newConsecutiveRolls = consecutiveNumbers + 1
                    if rollMax[newRoll - 1] < newConsecutiveRolls:
                        continue
                    else:
                        ifRollThis = dp(rollsLeft - 1, newConsecutiveRolls, newRoll)
                        resForThis += ifRollThis

            return resForThis % MOD
        return dp(n, 0, -1)