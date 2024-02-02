# https://leetcode.com/problems/out-of-boundary-paths/description/?envType=daily-question&envId=2024-01-26
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# There is an m x n grid with a ball. The ball is initially at the position [startRow, startColumn]. You are allowed to move the ball to one of the four adjacent cells in the grid (possibly out of the grid crossing the grid boundary). You can apply at most maxMove moves to the ball.

# Given the five integers m, n, maxMove, startRow, startColumn, return the number of paths to move the ball out of the grid boundary. Since the answer can be very large, return it modulo 109 + 7.

# Solution
# O(n*m*moves) time and space, standard dp

class Solution:
    def findPaths(self, m: int, n: int, maxMove: int, startRow: int, startColumn: int) -> int:
        DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
        MOD = 10**9 + 7

        height = m
        width = n

        @cache
        def dp(r, c, movesLeft):
            # base case
            if r < 0 or r == height or c < 0 or c == width:
                return 1
            if movesLeft == 0:
                return 0

            resThis = 0
            for rowDiff, colDiff in DIFFS:
                newRow = rowDiff + r
                newCol = colDiff + c
                resThis += dp(newRow, newCol, movesLeft - 1)
            return resThis % MOD

        return dp(startRow, startColumn, maxMove)

