# https://leetcode.com/problems/number-of-closed-islands/
# Difficulty: Medium
# Tags: matrix dfs

# Problem
# Given a 2D grid consists of 0s (land) and 1s (water).  An island is a maximal 4-directionally connected group of 0s and a closed island is an island totally (all left, top, right, bottom) surrounded by 1s.

# Return the number of closed islands.

# Solution, O(n*m) time and space
# Nearly copied code from 1020, just tell if an island has touched the border (switch names of land to water), if not, add to res. DFS and maintain seen.


class Solution:
    def closedIsland(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        seen = set() # so we don't duplicate islands

        diffs = [[1,0], [-1,0], [0,1], [0,-1] ]

        # dfs tells us if some child cell touched an edge, and the total number of cells we have in our island
        def dfs(r, c):
            seen.add(r * WIDTH + c)

            hasTouchedLandForThis = False

            for rowDiff, colDiff in diffs:
                newRow = rowDiff + r
                newCol = colDiff + c
                # skip out of bounds
                if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                    hasTouchedLandForThis = True
                    continue
                # skip water
                if grid[newRow][newCol] == 1:
                    continue
                # skip seen land
                if newRow * WIDTH + newCol in seen:
                    continue
                hasTouchedLandForAdj = dfs(newRow, newCol)
                hasTouchedLandForThis = hasTouchedLandForThis or hasTouchedLandForAdj
            return hasTouchedLandForThis
        res = 0
        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 1:
                    continue
                if r * WIDTH + c in seen:
                    continue
                canTouchLand = dfs(r, c)
                if not canTouchLand:
                    res += 1
        return res


