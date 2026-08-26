# https://leetcode.com/problems/sort-integers-by-the-power-value/description/
# difficulty: medium
# tags: dynamic programming 1d

# problem
# The power of an integer x is defined as the number of steps needed to transform x into 1 using the following steps:

# if x is even then x = x / 2
# if x is odd then x = 3 * x + 1
# For example, the power of x = 3 is 7 because 3 needs 7 steps to become 1 (3 --> 10 --> 5 --> 16 --> 8 --> 4 --> 2 --> 1).

# Given three integers lo, hi and k. The task is to sort all integers in the interval [lo, hi] by the power value in ascending order, if two or more integers have the same power value sort them by ascending order.

# Return the kth integer in the range [lo, hi] sorted by the power value.

# Notice that for any integer x (lo <= x <= hi) it is guaranteed that x will transform into 1 using these steps and that the power of x is will fit in a 32-bit signed integer.

# Solution, O(n * find power + n log n) time, O(max(power callstack, n)) space
# Find the power for each number. I have no proof for the upper bound on this.

class Solution:
    def getKth(self, lo: int, hi: int, k: int) -> int:
        @cache
        def getPower(n):
            # base case
            if n == 1:
                return 0
            if n % 2 == 0:
                return 1 + getPower(n / 2)
            return 1 + getPower(3*n + 1)

        powers = [] # stores [power, number]
        for i in range(lo, hi + 1):
            powers.append([getPower(i), i])
        powers.sort()
        return powers[k - 1][1]