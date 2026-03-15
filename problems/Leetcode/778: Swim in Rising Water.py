# https://leetcode.com/problems/swim-in-rising-water/description/
# Difficulty: Hard
# Tags: matrix dfs, binary search

# Problem
# You are given an n x n integer matrix grid where each value grid[i][j] represents the elevation at that point (i, j).

# The rain starts to fall. At time t, the depth of the water everywhere is t. You can swim from a square to another 4-directionally adjacent square if and only if the elevation of both squares individually are at most t. You can swim infinite distances in zero time. Of course, you must stay within the boundaries of the grid during your swim.

# Return the least time until you can reach the bottom right square (n - 1, n - 1) if you start at the top left square (0, 0).

# Solution O(log(max(grid)) * n^2) time, O(n^2) space
# Binary search for a time, then test if we can cross in n*m time and space.

class Solution:
    def swimInWater(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        def canCrossAtTime(time):
            if grid[0][0] > time:
                return False
            seen = set() # holds r * WIDTH + c
            diffs = [ [1,0], [-1,0], [0,1], [0,- 1] ]
            def dfs(r, c):
                seen.add(r * WIDTH + c)
                # base case
                if r == HEIGHT - 1 and c == WIDTH - 1:
                    return True

                for rowDiff, colDiff in diffs:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    key = newRow * WIDTH + newCol
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0 or grid[newRow][newCol] > time or key in seen:
                        continue
                    if dfs(newRow, newCol):
                        return True

                return False
            return dfs(0, 0)

        l = 0
        r = max(max(row) for row in grid)
        while l <= r:
            m = (r + l) // 2 # m is the time we try
            if canCrossAtTime(m):
                r = m - 1
            else:
                l = m + 1
        return r + 1



