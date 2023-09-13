# https://leetcode.com/problems/number-of-digit-one/description/
# Difficulty: Hard
# tags: digit dp

# Problem
# Given an integer n, count the total number of digit 1 appearing in all non-negative integers less than or equal to n.

# Solution, O(log(n) * log(n) * 2) space, 10 times that for time.
# We need the index, the total number of ones, and tight.

class Solution:
    def countDigitOne(self, n: int) -> int:
        strNum = str(n)
        @cache
        # memo[index][num ones][tight]
        def dp(i, numOnes, tight):
            # base case
            if i == len(strNum):
                return numOnes

            resForThis = 0
            upperBoundary = int(strNum[i]) if tight else 9
            for digit in range(upperBoundary + 1):
                newTight = tight and digit == upperBoundary
                newNumOnes = numOnes + 1 if digit == 1 else numOnes
                resForThis += dp(i + 1, newNumOnes, newTight)

            return resForThis
        return dp(0, 0, True)
