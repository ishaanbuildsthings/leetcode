# https://leetcode.com/problems/2-keys-keyboard/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# There is only one character 'A' on the screen of a notepad. You can perform one of two operations on this notepad for each step:

# Copy All: You can copy all the characters present on the screen (a partial copy is not allowed).
# Paste: You can paste the characters which are copied last time.
# Given an integer n, return the minimum number of operations to get the character 'A' exactly n times on the screen.

# Solution, O(n^2) time and space
# Normal DP, just try each option. I'm sure there's a more mathemtical solution that is faster.

class Solution:
    def minSteps(self, n: int) -> int:

        @cache
        def dp(currentChars, copiedAmount):
            # base case
            if currentChars == n:
                return 0

            resForThis = float('inf')
            # we can copy if we have a different amount
            if copiedAmount != currentChars:
                ifCopy = 1 + dp(currentChars, currentChars)
                resForThis = ifCopy

            # paste if it doesn't overflow, and we have a character to paste
            newCharsIfPaste = copiedAmount + currentChars
            if newCharsIfPaste <= n and copiedAmount > 0:
                ifPaste = 1 + dp(currentChars + copiedAmount, copiedAmount)
                resForThis = min(resForThis, ifPaste)

            return resForThis

        return dp(1, 0)