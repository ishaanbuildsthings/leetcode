# https://leetcode.com/problems/count-of-integers/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# You are given two numeric strings num1 and num2 and two integers max_sum and min_sum. We denote an integer x to be good if:

# num1 <= x <= num2
# min_sum <= digit_sum(x) <= max_sum.
# Return the number of good integers. Since the answer may be large, return it modulo 109 + 7.

# Note that digit_sum(x) denotes the sum of the digits of x.

# Solution, O(log(n) * 2 * 2 * 200) space, 2 times that for time. Could be sped up a bit with some pruning.
# We need i, nonZeroTaken though maybe we could just subtract one from the result, tight, the current sum of digits.

class Solution:
    def count(self, num1: str, num2: str, min_sum: int, max_sum: int) -> int:
        MOD = (10**9) + 7
        # memo[i][nonZeroTaken][isTight][prevSum]
        @cache
        def dp(i, nonZeroTaken, isTight, prevSum, strNum):
            # base case
            if i == len(strNum):
                if nonZeroTaken and prevSum >= min_sum:
                    return 1
                return 0

            resForThis = 0
            upperBoundary = int(strNum[i]) if isTight else 9
            for digit in range(upperBoundary + 1):
                # skip a digit if it would make the sum too big
                if digit + prevSum > max_sum:
                    continue
                newTight = isTight and digit == upperBoundary
                newSum = prevSum + digit
                newNonZeroTaken = nonZeroTaken or (digit != 0)
                resForThis += dp(i + 1, newNonZeroTaken, newTight, newSum, strNum)

            return resForThis

        return (dp(0, True, True, 0, num2) - dp(0, True, True, 0, str(int(num1) - 1))) % MOD