# https://leetcode.com/problems/knight-dialer/description/
# difficulty: medium
# tags: dynamic programming 2d

# problem
# The chess knight has a unique movement, it may move two squares vertically and one square horizontally, or two squares horizontally and one square vertically (with both forming the shape of an L). The possible movements of chess knight are shown in this diagaram:

# A chess knight can move as indicated in the chess diagram below:

# We have a chess knight and a phone pad as shown below, the knight can only stand on a numeric cell (i.e. blue cell).

# Given an integer n, return how many distinct phone numbers of length n we can dial.

# You are allowed to place the knight on any numeric cell initially and then you should perform n - 1 jumps to dial a number of length n. All jumps should be valid knight jumps.

# As the answer may be very large, return the answer modulo 109 + 7.

# Solution, O(n * 10 * 8) time, O(n * 10) space
# For each space, try moving to a valid new location with one fewer move.

COORDS = { 1 : [0, 0], 2 : [0, 1], 3 : [0, 2], 4 : [1, 0], 5 : [1, 1], 6 : [1, 2], 7 : [2, 0], 8: [2, 1], 9 : [2, 2], 0 : [3, 1] }
GRID = [ [1, 2, 3], [4, 5, 6], [7, 8, 9], [None, 0, None] ]

DIFFS = [ [1, 2], [-1, 2], [1, -2], [-1, -2], [2, 1], [2, -1], [-2, 1], [-2, -1] ]

MOD = 10**9 + 7

class Solution:
    def knightDialer(self, n: int) -> int:
        HEIGHT = 4
        WIDTH = 3

        @cache
        def dp(movesLeft, number):
            # base case
            if movesLeft == 0:
                return 1

            resForThis = 0

            row, col = COORDS[number]
            for rowDiff, colDiff in DIFFS:
                newRow = row + rowDiff
                newCol = col + colDiff
                if newRow == 3 and (newCol == 0 or newCol == 2):
                    continue
                if newRow >= 0 and newRow < HEIGHT and newCol >= 0 and newCol < WIDTH:
                    resForThis += dp(movesLeft - 1, GRID[newRow][newCol])

            return resForThis % MOD

        res = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if r == 3 and c == 0:
                    continue
                if r == 3 and c == 2:
                    continue
                res += dp(n - 1, GRID[r][c])
                res %= MOD
        return res





