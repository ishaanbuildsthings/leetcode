# https://leetcode.com/problems/detect-cycles-in-2d-grid/description/
# difficulty: medium
# tags: graph, matrix dfs

# Problem
# Given a 2D array of characters grid of size m x n, you need to find if there exists any cycle consisting of the same value in grid.

# A cycle is a path of length 4 or more in the grid that starts and ends at the same cell. From a given cell, you can move to one of the cells adjacent to it - in one of the four directions (up, down, left, or right), if it has the same value of the current cell.

# Also, you cannot move to the cell that you visited in your last move. For example, the cycle (1, 1) -> (1, 2) -> (1, 1) is invalid because from (1, 2) we visited (1, 1) which was the last visited cell.

# Return true if any cycle of the same value exists in grid, otherwise, return false.

# Solution
# We can dfs from every cell (skip from our root dfs calls if we have already seen). If we ever see a cell twice, that isn't the one we just came from, we have a cycle. O(n*m) time and space. Note we can also have dfs be haveCycle and use that to terminate early, rather than the cycleFound pruning.

DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
class Solution:
    def containsCycle(self, grid: List[List[str]]) -> bool:
        height = len(grid)
        width = len(grid[0])

        seen = set()
        cycleFound = False # pruning

        # NOTE, WE CAN ALSO MAKE DFS be haveCycle AND IT RETURNS IF IT HAS A CYCLE FROM THAT POINT, THEN WE CAN DO:
        # if dfs(child coordinates): return True
        # to bubble things up, instead of using a global variable

        def dfs(r, c, val, lastPos):
            nonlocal cycleFound

            if cycleFound:
                return

            seen.add((r, c))
            for rowDiff, colDiff in DIFFS:
                newRow = rowDiff + r
                newCol = colDiff + c
                # skip out of bounds
                if newRow == height or newRow < 0 or newCol == width or newCol < 0:
                    continue
                # skip wrong values
                if grid[newRow][newCol] != val:
                    continue
                # skip the cell we were just at
                if (newRow, newCol) == lastPos:
                    continue
                # if we find a cycle
                if (newRow, newCol) in seen:
                    cycleFound = True
                    return
                dfs(newRow, newCol, val, (r, c))


        for r in range(height):
            for c in range(width):
                if (r, c) in seen:
                    continue
                dfs(r, c, grid[r][c], (None, None))
                if cycleFound:
                    return True
        return False


