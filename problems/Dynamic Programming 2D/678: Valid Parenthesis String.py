# https://leetcode.com/problems/valid-parenthesis-string/description/
# difficulty: medium
# tags: dynamic programming 2d

# problem
# Given a string s containing only three types of characters: '(', ')' and '*', return true if s is valid.

# The following rules define a valid string:

# Any left parenthesis '(' must have a corresponding right parenthesis ')'.
# Any right parenthesis ')' must have a corresponding left parenthesis '('.
# Left parenthesis '(' must go before the corresponding right parenthesis ')'.
# '*' could be treated as a single right parenthesis ')' or a single left parenthesis '(' or an empty string "".

# Solution, O(n^2) time and space
# As we iterate, track the counts. For each * we can try either. We could probably reduce the callstack size by jumping to the next *

class Solution:
    def checkValidString(self, s: str) -> bool:
        @cache
        def dp(i, leftSurplus):
            # base case
            if i == len(s):
                return leftSurplus == 0


            if s[i] == '(':
                return dp(i + 1, leftSurplus + 1)

            if s[i] == ')':
                # can never exceed )
                if leftSurplus - 1 < 0:
                    return False
                return dp(i + 1, leftSurplus - 1)

            if leftSurplus - 1 < 0:
                return dp(i + 1, leftSurplus + 1) or dp(i + 1, leftSurplus)

            return dp(i + 1, leftSurplus + 1) or dp(i + 1, leftSurplus - 1) or dp(i + 1, leftSurplus)
        return dp(0, 0)

