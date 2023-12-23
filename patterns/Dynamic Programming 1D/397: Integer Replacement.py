# https://leetcode.com/problems/integer-replacement/
# difficulty: medium
# tags: dynamic programming 1d

# Problem
# Given a positive integer n, you can apply one of the following operations:

# If n is even, replace n with n / 2.
# If n is odd, replace n with either n + 1 or n - 1.
# Return the minimum number of operations needed for n to become 1.

# Solution, O(log n) time and space, we have log n states since each halving only requires at most one extra state, we can cache since there can be overlapping states

class Solution:
    def integerReplacement(self, n: int) -> int:
        @cache
        def dp(numLeft):
            # base case
            if numLeft == 1:
                return 0

            if numLeft % 2 == 0:
                return 1 + dp(int(numLeft / 2))

            return 1 + min(dp(numLeft + 1), dp(numLeft - 1))

        return dp(n)