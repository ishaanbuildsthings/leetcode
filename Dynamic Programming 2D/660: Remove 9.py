# https://leetcode.com/problems/remove-9/description/
# difficulty: hard
# tags: digit dp, math

# Problem
# Start from integer 1, remove any integer that contains 9 such as 9, 19, 29...

# Now, you will have a new integer sequence [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, ...].

# Given an integer n, return the nth (1-indexed) integer in the new sequence.

# Solution
# If n=15, normally it's the 15th number. But we can count the number of numbers with a 9 from [1, 15], then we need to add on to 15. I did that recursively in a loop using digit dp.
# Solution 2: Since we remove one digit, we just convert the base, so we could rewrite in base 9.

class Solution:
    def newInteger(self, n: int) -> int:
        @cache
        def dp(i, tight, hasNine, strNum):
            # base case
            if i == len(strNum):
                return 1 if hasNine else 0

            upperBoundary = int(strNum[i]) if tight else 9

            resForThis = 0

            for nextDigit in range(upperBoundary + 1):
                newTight = tight and str(nextDigit) == strNum[i]
                newHasNine = hasNine or nextDigit == 9
                resForThis += dp(i + 1, newTight, newHasNine, strNum)

            return resForThis

        def numNines(low, high):
            highCount = dp(0, True, False, str(high))
            # dp.cache_clear() # depends what you want to do, maximize time for memory tradeoff
            lowCount = dp(0, True, False, str(low - 1))
            # dp.cache_clear()
            return highCount - lowCount

        nextLow = 1
        remaining = n

        while remaining:
            # we assume that we use remaining numbers starting from nextLow, yielding some temp value
            temp = remaining + nextLow - 1

            # for that temp value, we check the amount of nine numbers that existed
            amount = numNines(nextLow, temp)

            # say we had n=100 at first but 6 numbers had a 9, now we have n=6 to go
            remaining = amount
            nextLow = temp + 1

        return nextLow - 1


