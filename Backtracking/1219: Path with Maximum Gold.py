# https://leetcode.com/problems/path-with-maximum-gold/description/
# difficulty: medium
# tags: backtracking

# problem
# In a gold mine grid of size m x n, each cell in this mine has an integer representing the amount of gold in that cell, 0 if it is empty.

# Return the maximum amount of gold you can collect under the conditions:

# Every time you are located in a cell you will collect all the gold in that cell.
# From your position, you can walk one step to the left, right, up, or down.
# You can't visit the same cell more than once.
# Never visit a cell with 0 gold.
# You can start and stop collecting gold from any position in the grid that has some gold.

# Solution, n*m*3^k time, as worst case we can go to three adjacent states (except for the first cell), and k<=25 is the number of cells with gold. Our callstack is of depth k so k space.

class Solution:
    def getMaximumGold(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        res = 0
        path = set()
        diffs = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
        def recurse(r, c):
            path.add(r * WIDTH + c)
            bestResult = grid[r][c]
            for rowDiff, colDiff in diffs:
                newRow = rowDiff + r
                newCol = colDiff + c
                # skip out of bounds
                if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                    continue
                # skip ones in the path
                if newRow * WIDTH + newCol in path:
                    continue
                # skip empty
                if grid[newRow][newCol] == 0:
                    continue
                bestResult = max(bestResult, grid[r][c] + recurse(newRow, newCol))
            path.remove(r * WIDTH + c)
            return bestResult

        res = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 0:
                    continue
                res = max(res, recurse(r, c))
        return res


