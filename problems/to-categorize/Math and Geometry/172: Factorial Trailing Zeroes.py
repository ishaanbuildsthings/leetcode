# https://leetcode.com/problems/factorial-trailing-zeroes/description/
# difficulty: medium
# tags: math

# Problem
# Given an integer n, return the number of trailing zeroes in n!.

# Note that n! = n * (n - 1) * (n - 2) * ... * 3 * 2 * 1.

# Solution
# A 0 is made with a 2 and a 5, so we count those for each one, which takes log time for each. n * log n final time. I cached the factorial counting which is O(n) space I think it can be reduced to log space though without @cache since if we hit a base case we don't need to cache that (can just catch that outside before we call the @cache funciton). There is a logN solution where we decompose n! into pieces I think.

class Solution:
    def trailingZeroes(self, n: int) -> int:
        @cache
        def getDivisorCount(num, divisor):
            if num == 0:
                return 0
            if num % divisor != 0:
                return 0
            return 1 + getDivisorCount(int(num / divisor), divisor)

        twoCount = 0
        fiveCount = 0

        for i in range(n + 1):
            twoCount += getDivisorCount(i, 2)
            fiveCount += getDivisorCount(i, 5)

        return min(twoCount, fiveCount)