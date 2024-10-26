# https://leetcode.com/problems/removing-stars-from-a-string/description/
# difficulty: medium
# tags: stack

# problem
# You are given a string s, which contains stars *.

# In one operation, you can:

# Choose a star in s.
# Remove the closest non-star character to its left, as well as remove the star itself.
# Return the string after all stars have been removed.

# Note:

# The input will be generated such that the operation is always possible.
# It can be shown that the resulting string will always be unique.

# Solution, O(n) time and space, just iterate, and when we get a store pop from the stack

class Solution:
    def removeStars(self, s: str) -> str:
        stack = []
        for char in s:
            if char == '*' and stack:
                stack.pop()
                continue
            stack.append(char)
        return ''.join(stack)