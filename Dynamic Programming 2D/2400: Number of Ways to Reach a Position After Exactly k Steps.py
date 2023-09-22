# https://leetcode.com/problems/number-of-ways-to-reach-a-position-after-exactly-k-steps/
# Difficulty: Medium
# Tags: dynamic programming 2d

# Problem
# You are given two positive integers startPos and endPos. Initially, you are standing at position startPos on an infinite number line. With one step, you can move either one position to the left, or one position to the right.

# Given a positive integer k, return the number of different ways to reach the position endPos starting from startPos, such that you perform exactly k steps. Since the answer may be very large, return it modulo 109 + 7.

# Two ways are considered different if the order of the steps made is not exactly the same.

# Note that the number line includes negative integers.

# Solution, n^2 time and space
# Easy dp, just move left or right!

class Solution:
    def numberOfWays(self, startPos: int, endPos: int, k: int) -> int:
        @cache
        def dp(pos, stepsPerformed):
            # base case
            if stepsPerformed == k:
                return 1 if pos == endPos else 0
            return dp(pos + 1, stepsPerformed + 1) + dp(pos - 1, stepsPerformed + 1)
        return dp(startPos, 0) % (10**9 + 7)