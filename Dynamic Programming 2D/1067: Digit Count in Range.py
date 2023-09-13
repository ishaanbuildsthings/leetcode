# https://leetcode.com/problems/digit-count-in-range/
# Difficulty: Hard
# Tags: digit dp

# Problem
# Given a single-digit integer d and two integers low and high, return the number of times that d occurs as a digit in all integers in the inclusive range [low, high].

# Solution, O(log(n) * 2 * 2 * amount of digit) space, 10 times that for time.
# We need the index we insert at, if we are tight, and if we have taken a non zero. This is useful if the digit we are searching is 0, since we only count it once we have not taken a non zero. We also need the total amount of digits. To go from [low, high] instead of [1, n] we can just range query.

class Solution:
    def digitsCount(self, d: int, low: int, high: int) -> int:
        # memo[i][tight][nonZeroTaken][prev amount of digit]
        @cache
        def dp(i, tight, nonZeroTaken, prevAmount, strNum):
            # base case
            if i == len(strNum):
                return prevAmount if nonZeroTaken else 0

            resForThis = 0
            upperBoundary = int(strNum[i]) if tight else 9
            for digit in range(upperBoundary + 1):
                newTight = tight and digit == upperBoundary
                newNonZeroTaken = nonZeroTaken or (digit != 0)
                # don't count a 0 if that is our target digit and we are still leading
                if not nonZeroTaken and digit == 0:
                    newAmount = 0
                else:
                    newAmount = prevAmount + 1 if digit == d else prevAmount
                resForThis += dp(i + 1, newTight, newNonZeroTaken, newAmount, strNum)

            return resForThis

        highAmount = dp(0, True, False, 0, str(high))
        dp.cache_clear()
        lowAmount = dp(0, True, False, 0, str(int(low) - 1))
        return highAmount - lowAmount