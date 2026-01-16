# https://leetcode.com/problems/magic-squares-in-grid/description/
# Difficulty: Medium

# Problem
# A 3 x 3 magic square is a 3 x 3 grid filled with distinct numbers from 1 to 9 such that each row, column, and both diagonals all have the same sum.

# Given a row x col grid of integers, how many 3 x 3 "magic square" subgrids are there?  (Each subgrid is contiguous).

# Solution, O(n*m) time, O(1) space
# Just check each 3x3 grid

class Solution:
    def numMagicSquaresInside(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        def isMagicSquare(topLeft):
            r1, c1 = topLeft
            r2 = r1 + 2 # bottom right coords
            c2 = c1 + 2
            sameSum = grid[r1][c1] + grid[r1][c1 + 1] + grid[r1][c1 + 2]
            # check distinct values
            vals = set()
            for r in range(r1, r1 + 3):
                for c in range(c1, c1 + 3):
                    if grid[r][c] in vals:
                        return False
                    if grid[r][c] > 9 or grid[r][c] < 1:
                        return False
                    vals.add(grid[r][c])
            # check rows
            for row in range(r1 + 1, r1 + 3):
                sumForRow = grid[row][c1] + grid[row][c1 + 1] + grid[row][c1 + 2]
                if sumForRow != sameSum:
                    return False
            # check columns
            for col in range(c1, c1 + 3):
                sumForCol = grid[r1][col] + grid[r1 + 1][col] + grid[r1 + 2][col]
                if sumForCol != sameSum:
                    return False
            # check diagonals
            if grid[r1][c1] + grid[r1 + 1][c1 + 1] + grid[r2][c2] != sameSum:
                return False
            if grid[r1 + 2][c1] + grid[r1 + 1][c1 + 1] + grid[r1][c1 + 2] != sameSum:
                return False
            return True
        res = 0
        for row in range(HEIGHT - 2):
            for col in range(WIDTH - 2):
                if isMagicSquare([row, col]):
                    res += 1
        return res
