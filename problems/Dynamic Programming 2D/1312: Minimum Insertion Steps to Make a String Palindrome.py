# https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/description/
# difficulty: hard
# tags: dynamic programming 2d

# problem
# Given a string s. In one step you can insert any character at any index of the string.

# Return the minimum number of steps to make s palindrome.

# A Palindrome String is one that reads the same backward as well as forward.

# Solution, O(n^2) time and space
# If the first and last letters are the same, take the middle subproblem. Otherwise try two other subproblems.

class Solution:
    def minInsertions(self, s: str) -> int:
        @cache
        def dp(l, r):
            # base cases
            if l >= r:
                return 0

            # if the ending characters are the same, we reduce
            if s[l] == s[r]:
                return dp(l + 1, r - 1)

            # otherwise, we can either add our char to the end
            ifAddToEnd = 1 + dp(l + 1, r)
            # or prepend it
            ifAddToBeginning = 1 + dp(l, r - 1)
            return min(ifAddToEnd, ifAddToBeginning)
        return dp(0, len(s) - 1)
