# https://leetcode.com/problems/island-perimeter/description/
# difficulty: easy
# tags: functional, graph

# Problem
# You are given row x col grid representing a map where grid[i][j] = 1 represents land and grid[i][j] = 0 represents water.

# Grid cells are connected horizontally/vertically (not diagonally). The grid is completely surrounded by water, and there is exactly one island (i.e., one or more connected land cells).

# The island doesn't have "lakes", meaning the water inside isn't connected to the water around the island. One cell is a square with side length 1. The grid is rectangular, width and height don't exceed 100. Determine the perimeter of the island.

# Solution, O(n*m) time, O(1) space, count edges for everything

DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
class Solution:
    def islandPerimeter(self, grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])

        def inBounds(r, c):
            return height > r >= 0 <= c < width

        def getEdges(r, c):
            return sum(
                1 if not inBounds(r + rowDiff, c + colDiff) or
                not grid[r + rowDiff][c + colDiff] else
                0
                for rowDiff, colDiff in DIFFS
            )

        return sum(
            getEdges(r, c)
            if grid[r][c]
            else 0
            for r in range(height)
            for c in range(width)
        )