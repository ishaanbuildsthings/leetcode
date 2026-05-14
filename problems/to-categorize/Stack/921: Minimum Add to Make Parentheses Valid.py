# https://leetcode.com/problems/minimum-add-to-make-parentheses-valid/description/
# difficulty: medium
# tags: stack

# problem
# A parentheses string is valid if and only if:

# It is the empty string,
# It can be written as AB (A concatenated with B), where A and B are valid strings, or
# It can be written as (A), where A is a valid string.
# You are given a parentheses string s. In one move, you can insert a parenthesis at any position of the string.

# For example, if s = "()))", you can insert an opening parenthesis to be "(()))" or a closing parenthesis to be "())))".
# Return the minimum number of moves required to make s valid.

# Solution, for every extra ( at the end, we need a parenthesis. For every time we try to add a ) with no corresponding prior (, we need one.

class Solution:
    def minAddToMakeValid(self, s: str) -> int:
        res = 0
        leadingLefties = 0
        for char in s:
            if char == '(':
                leadingLefties += 1
            elif char == ')':
                if leadingLefties > 0:
                    leadingLefties -= 1
                else:
                    res += 1
        return res + leadingLefties
