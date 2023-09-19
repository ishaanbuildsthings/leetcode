# https://leetcode.com/problems/handshakes-that-dont-cross/description/
# Difficulty: Hard
# Tags: Dynamic Programming 1d

# Problem
# You are given an even number of people numPeople that stand around a circle and each person shakes hands with someone else so that there are numPeople / 2 handshakes total.

# Return the number of ways these handshakes could occur such that none of the handshakes cross.

# Since the answer could be very large, return it modulo 109 + 7.

# Solution, O(n^2) time and O(n) space
# Whenever a handshake is made, we split into two smaller circles. Easy dp!

class Solution:
    def numberOfWays(self, numPeople: int) -> int:
        MOD = 10**9 + 7
        # when we make a handshake, we divide into two circlular groups
        @cache
        def dp(peopleLeft):
            # base case
            if peopleLeft == 0:
                return 1

            # if we have an even number of people left, say 6, and we are person 1, we can only shake hands with person 2, 4, or 6
            resForThis = 0
            for i in range(2, peopleLeft + 1, 2):
                peopleOnLeft = i - 2
                peopleOnRight = peopleLeft - i
                waysForThis = dp(peopleOnLeft) * dp(peopleOnRight)
                resForThis += waysForThis

            return resForThis % MOD

        return dp(numPeople)