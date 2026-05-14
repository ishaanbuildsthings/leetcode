# https://leetcode.com/problems/check-if-there-is-a-valid-path-in-a-grid/
# difficulty: medium
# tags: graph, matrix dfs

# problem
# You are given an m x n grid. Each cell of grid represents a street. The street of grid[i][j] can be:

# 1 which means a street connecting the left cell and the right cell.
# 2 which means a street connecting the upper cell and the lower cell.
# 3 which means a street connecting the left cell and the lower cell.
# 4 which means a street connecting the right cell and the lower cell.
# 5 which means a street connecting the left cell and the upper cell.
# 6 which means a street connecting the right cell and the upper cell.
# You will initially start at the street of the upper-left cell (0, 0). A valid path in the grid is a path that starts from the upper left cell (0, 0) and ends at the bottom-right cell (m - 1, n - 1). The path should only follow the streets.

# Notice that you are not allowed to change any street.

# Return true if there is a valid path in the grid or false otherwise.

# Solution, O(n*m) time and space
# DFS out as far as we can, track seen cells to not duplicate.

class Solution:
    def hasValidPath(self, grid: List[List[int]]) -> bool:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])
        diffs = [[1,0],[-1,0],[0,1],[0,-1]]

        streets = {
            1: ['l', 'r'],
            2 : ['u', 'd'],
            3 : ['l', 'd'],
            4: ['r', 'd'],
            5: ['l', 'u'],
            6 : ['u', 'r'],
        }
        depToArr = {
            'd' : 'u',
            'u' : 'd',
            'r' : 'l',
            'l' : 'r'
        }

        seen = set() # don't repeat work

        def dfs(r, c):
            key = r * WIDTH + c
            seen.add(key)
            # base case
            if r == HEIGHT - 1 and c == WIDTH - 1:
                return True
            for rowDiff, colDiff in diffs:
                newRow = rowDiff + r
                newCol = colDiff + c
                newKey = newRow * WIDTH + newCol
                # skip out of bounds
                if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                    continue
                # skip seen
                if newKey in seen:
                    continue

                # determine departure direction
                if rowDiff == 1:
                    departureDirection = 'd'
                elif rowDiff == -1:
                    departureDirection = 'u'
                if colDiff == 1:
                    departureDirection = 'r'
                elif colDiff == -1:
                    departureDirection = 'l'
                arrivalDirection = depToArr[departureDirection]

                # skip invalid rows
                if not departureDirection in streets[grid[r][c]] or not arrivalDirection in streets[grid[newRow][newCol]]:
                    continue

                if dfs(newRow, newCol):
                    return True
            return False
        return dfs(0, 0)





