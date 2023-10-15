# https://leetcode.com/problems/number-of-ways-to-stay-in-the-same-place-after-some-steps/description/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# You have a pointer at index 0 in an array of size arrLen. At each step, you can move 1 position to the left, 1 position to the right in the array, or stay in the same place (The pointer should not be placed outside the array at any time).

# Given two integers steps and arrLen, return the number of ways such that your pointer is still at index 0 after exactly steps steps. Since the answer may be too large, return it modulo 109 + 7.


# Solution, O(steps ^ 2) time and space, just try each movement. We could prune more aggressively by terminating states that could not reach 0 in time.

MOD = 10**9 + 7

class Solution:
    def numWays(self, steps: int, arrLen: int) -> int:
        @cache
        def dp(stepsUsed, position):
            # base case
            if stepsUsed == steps:
                return 1 if position == 0 else 0

            resForThis = 0

            if position - 1 >= 0:
                resForThis += dp(stepsUsed + 1, position - 1)
            if position + 1 < arrLen:
                resForThis += dp(stepsUsed + 1, position + 1)
            resForThis += dp(stepsUsed + 1, position)

            return resForThis % MOD

        return dp(0, 0)



