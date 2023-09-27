# https://leetcode.com/problems/check-if-number-is-a-sum-of-powers-of-three/description/
# difficulty: medium
# tags: dynamic programming 2d, greedy

# problem
# Given an integer n, return true if it is possible to represent n as the sum of distinct powers of three. Otherwise, return false.

# An integer y is a power of three if there exists an integer x such that y == 3x.

# Solution, O(log n * unique sums) time and space
# I generated all powers of 3 < n which is log n overhead time and space. Then, for each log n, we have some target left. So we have log n * unique sum states and time.
#* Though greedy does work, just taking the largest powers of 3 first, like a ternary representation of our number.
pows = []
power = 0
while True:
    nextPower = 3**power
    if nextPower > 10**7:
        break
    pows.append(3**power)
    power += 1

class Solution:
    def checkPowersOfThree(self, n: int) -> bool:
        @cache
        def dp(i, targetLeft):
            # base case
            if targetLeft == 0:
                return True
            if i == len(pows):
                return False
            # pruning
            if targetLeft < pows[i]:
                return False

            ifTake = dp(i + 1, targetLeft - pows[i])
            if ifTake:
                return True
            ifSkip = dp(i + 1, targetLeft)
            return ifSkip
        return dp(0, n)

