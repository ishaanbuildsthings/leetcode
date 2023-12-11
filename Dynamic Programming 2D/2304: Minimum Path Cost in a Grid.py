# https://leetcode.com/problems/minimum-path-cost-in-a-grid/description/
# difficulty: medium
# tags: dynamic programming 2d

# Problem
# You are given a 0-indexed m x n integer matrix grid consisting of distinct integers from 0 to m * n - 1. You can move in this matrix from a cell to any other cell in the next row. That is, if you are in cell (x, y) such that x < m - 1, you can move to any of the cells (x + 1, 0), (x + 1, 1), ..., (x + 1, n - 1). Note that it is not possible to move from cells in the last row.

# Each possible move has a cost given by a 0-indexed 2D array moveCost of size (m * n) x n, where moveCost[i][j] is the cost of moving from a cell with value i to a cell in column j of the next row. The cost of moving from cells in the last row of grid can be ignored.

# The cost of a path in grid is the sum of all values of cells visited plus the sum of costs of all the moves made. Return the minimum cost of a path that starts from any cell in the first row and ends at any cell in the last row.

# Solution, O(r*c*c) time, O(r*c) space, we can space optimize to linear with bottom up.

class Solution:
    def minPathCost(self, grid: List[List[int]], moveCost: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])

        @cache
        def dp(r, c):
            # base case
            if r == height - 1:
                return 0

            val = grid[r][c]

            return min(
                moveCost[val][c] + grid[r + 1][c] + dp(r + 1, c)
                for c in range(width)
            )

        return min(grid[0][c] + dp(0, c) for c in range(width))