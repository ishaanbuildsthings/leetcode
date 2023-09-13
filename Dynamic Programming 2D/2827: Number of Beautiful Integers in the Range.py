# https://leetcode.com/problems/number-of-beautiful-integers-in-the-range/description/
# Difficulty: Hard
# Tags: digit dp

# Problem
# You are given positive integers low, high, and k.

# A number is beautiful if it meets both of the following conditions:

# The count of even digits in the number is equal to the count of odd digits.
# The number is divisible by k.
# Return the number of beautiful integers in the range [low, high].

# Solution, O(log(n) * 2 * 2 * log(n) * log(n) * k) space, 10 times that for time.
# We need the typical index of insertion, is tight, and non zero taken (we only count 0s as an even once we have taken a non zero). We also track the odd count and even count. There is pruning that can be done if we have too much a surplus of one. We could also just use a surplus parameter. We also need the remainder. Every time we take a digit, say in _ _ _ we take a 1, we are really adding 100, and if k is 3 we are adding a remainder of 1, so that is how we maintain the remainder parameter.

class Solution:
    def numberOfBeautifulIntegers(self, low: int, high: int, k: int) -> int:
        # memo[i][tight][non zero taken][odd count][even count][remainder]
        @cache
        def dp(i, tight, nonZeroTaken, oddCount, evenCount, remainder, strNum):
            # base case
            if i == len(strNum):
                return 1 if nonZeroTaken and remainder == 0 and oddCount == evenCount else 0

            resForThis = 0

            upperBoundary = int(strNum[i]) if tight else 9
            for digit in range(upperBoundary + 1):
                newTight = tight and digit == upperBoundary
                newNonZeroTaken = nonZeroTaken or digit != 0
                newOddCount = oddCount + 1 if (digit % 2 == 1) else oddCount
                if not nonZeroTaken and digit == 0:
                    newEvenCount = evenCount # don't count a 0 if it's a leading zero
                else:
                    newEvenCount = evenCount + 1 if (digit % 2 == 0) else evenCount
                newRemainderDiff = (digit * (10**(len(strNum) - 1 - i))) % k
                newRemainder = (remainder + newRemainderDiff) % k
                resForThis += dp(i + 1, newTight, newNonZeroTaken, newOddCount, newEvenCount, newRemainder, strNum)

            return resForThis

        highCount = dp(0, True, False, 0, 0, 0, str(high))
        lowCount = dp(0, True, False, 0, 0, 0, str(low - 1))
        return highCount - lowCount

