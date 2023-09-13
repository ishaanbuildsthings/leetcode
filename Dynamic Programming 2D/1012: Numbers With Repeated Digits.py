# https://leetcode.com/problems/numbers-with-repeated-digits/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# Given an integer n, return the number of positive integers in the range [1, n] that have at least one repeated digit.

# Solution, O(log(n) * 2 * 2 * 2^log(n) * 2) space, 10 times that for time.
# We need the index we are inserting the number at, if we have taken a non zero yet (we need this to know if taking a 0 should count as a repeat, since leading 0s should not), a bitmask of which digits have been taken, and if we have repeated a digit yet.

class Solution:
    def numDupDigitsAtMostN(self, n: int) -> int:
        strNum = str(n)
        # memo[i][nonZeroTaken][tight][digit mask][hasRepeated]
        @cache
        def dp(i, nonZeroTaken, tight, mask, hasRepeated):
            # base case
            if i == len(strNum):
                return 1 if hasRepeated and nonZeroTaken else 0

            resForThis = 0
            upperBoundary = int(strNum[i]) if tight else 9
            for digit in range(upperBoundary + 1):
                newTight = tight and digit == upperBoundary
                newNonZeroTaken = nonZeroTaken or (digit != 0)
                newHasRepeated = hasRepeated or (((mask >> digit) & 1) and not (not nonZeroTaken and digit == 0))
                # if our only zeroes were leading zeroes before, adding a new zero doesn't trigger repeated, e.g. 010
                if not nonZeroTaken and digit == 0:
                    newMask = 0
                else:
                    newMask = mask | (1 << digit)
                resForThis += dp(i + 1, newNonZeroTaken, newTight, newMask, newHasRepeated)
            return resForThis

        return dp(0, False, True, 0, False)