# https://leetcode.com/problems/cherry-pickup-ii/
# difficulty: hard
# tags: dynamic programming 2d

# Problem
# You are given a rows x cols matrix grid representing a field of cherries where grid[i][j] represents the number of cherries that you can collect from the (i, j) cell.

# You have two robots that can collect cherries for you:

# Robot #1 is located at the top-left corner (0, 0), and
# Robot #2 is located at the top-right corner (0, cols - 1).
# Return the maximum number of cherries collection using both robots by following the rules below:

# From a cell (i, j), robots can move to cell (i + 1, j - 1), (i + 1, j), or (i + 1, j + 1).
# When any robot passes through a cell, It picks up all cherries, and the cell becomes an empty cell.
# When both robots stay in the same cell, only one takes the cherries.
# Both robots cannot move outside of the grid at any moment.
# Both robots should reach the bottom row in grid.

# Solution, O(height*width^2) time and space, standard dp, typed this on my phone lol

class Solution:
    def cherryPickup(self, grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])
        @cache
        def dp(r, c1, c2):
            # base
            if r == height:
                return 0
            resThis = 0
            for dir1 in range(3):
                for dir2 in range(3):
                    newC1 = c1 + dir1 - 1
                    newC2 = c2 + dir2 - 1
                    if newC1 < 0 or newC1 == width or newC2 < 0 or newC2 == width:
                        continue
                    resThis = max(resThis, dp(r+1,newC1,newC2) + grid[r][c1] + grid[r][c2] if c2 != c1 else 0)
            return resThis
        return dp(0,0,width-1)
