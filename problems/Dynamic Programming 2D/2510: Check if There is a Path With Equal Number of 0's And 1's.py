# https://leetcode.com/problems/check-if-there-is-a-path-with-equal-number-of-0s-and-1s/description/
# difficulty: medium
# tags: dynamic programming 2d, greedy

# Problem
# You are given a 0-indexed m x n binary matrix grid. You can move from a cell (row, col) to any of the cells (row + 1, col) or (row, col + 1).

# Return true if there is a path from (0, 0) to (m - 1, n - 1) that visits an equal number of 0's and 1's. Otherwise return false.

# Solution, cubed time and space, there is a squared one (codeforces solution)

class Solution:
    def isThereAPath(self, grid: List[List[int]]) -> bool:
        height = len(grid)
        width = len(grid[0])

        # can be done in n*m time with the codeforces solution

        @cache
        def dp(r, c, zeroSurplus):

            # base
            if r == height - 1 and c == width - 1:
                return not zeroSurplus

            resThis = False

            # down
            if r + 1 < height:
                resThis = dp(r + 1, c, zeroSurplus + (1 if not grid[r + 1][c] else -1))

            # right
            if c + 1 < width and not resThis:
                resThis = dp(r, c + 1, zeroSurplus + (1 if not grid[r][c + 1] else -1))

            return resThis

        return dp(0, 0, -1 if grid[0][0] else 1)

