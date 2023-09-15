# https://leetcode.com/problems/check-if-there-is-a-valid-parentheses-string-path/description/
# Difficulty: Hard
# Tags: Dynamic Programming 2d

# Problem
# A parentheses string is a non-empty string consisting only of '(' and ')'. It is valid if any of the following conditions is true:

# It is ().
# It can be written as AB (A concatenated with B), where A and B are valid parentheses strings.
# It can be written as (A), where A is a valid parentheses string.
# You are given an m x n matrix of parentheses grid. A valid parentheses string path in the grid is a path satisfying all of the following conditions:

# The path starts from the upper left cell (0, 0).
# The path ends at the bottom-right cell (m - 1, n - 1).
# The path only ever moves down or right.
# The resulting parentheses string formed by the path is valid.
# Return true if there exists a valid parentheses string path in the grid. Otherwise, return false.

# Solution, O(m*n*min(m, n)) time, O(m*n*min(m, n)) space
# Note that to build a valid string path, we need equal ( to ), and at any point we cannot exceed ). So we make a DP for each cell, which cells us if its valid, given a prior surplus of (. If the surplus is ever negative meaning we have more ), it is an instant fail.

class Solution:
    def hasValidPath(self, grid: List[List[str]]) -> bool:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        @cache
        def dp(r, c, surplusOfLeft):
            # base case, we are at the bottom right
            if r == HEIGHT - 1 and c == WIDTH - 1 and surplusOfLeft == 0:
                return True
            # if we ever have more ) than (, we are automatically invalid
            if surplusOfLeft < 0:
                return False

            # if the bottom cell is in range and doable
            if r + 1 < HEIGHT:
                if dp(r + 1, c, surplusOfLeft + 1 if grid[r+1][c] == '(' else surplusOfLeft - 1):
                    return True

            # if the right cell is in range and doable
            if c + 1 < WIDTH:
                if dp(r, c + 1, surplusOfLeft + 1 if grid[r][c+1] == '(' else surplusOfLeft - 1):
                    return True


            return False

        return dp(0, 0, 1 if grid[0][0] == '(' else -1)
