# https://leetcode.com/problems/path-with-minimum-effort/description/?envType=daily-question&envId=2023-09-16
# Difficulty: Medium
# Tags: matrix dfs, binary search

# Problem
# You are a hiker preparing for an upcoming hike. You are given heights, a 2D array of size rows x columns, where heights[row][col] represents the height of cell (row, col). You are situated in the top-left cell, (0, 0), and you hope to travel to the bottom-right cell, (rows-1, columns-1) (i.e., 0-indexed). You can move up, down, left, or right, and you wish to find a route that requires the minimum effort.

# A route's effort is the maximum absolute difference in heights between two consecutive cells of the route.

# Return the minimum effort required to travel from the top-left cell to the bottom-right cell.

# Solution, log 10^6 * m * n time, O(m*n) space

# At the worst, our effort is 10^6 which is a max cell value. We binary search on that. For each attempt at constraining to an effort, we try to dfs to the end, caching what we have visited.

class Solution:
    def minimumEffortPath(self, heights: List[List[int]]) -> int:
        HEIGHT = len(heights)
        WIDTH = len(heights[0])

        def canCrossPathWithinEffort(effort):

            visited = set() # stores row * WIDTH + col
            diffs = [[1,0], [-1,0], [0,1], [0,-1] ]
            def dfs(r, c):
                # base case
                if r == HEIGHT - 1 and c == WIDTH - 1:
                        return True

                visited.add(r * WIDTH + c)
                for rowDiff, colDiff in diffs:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    # cannot go out of bounds
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                        continue
                    # cannot go to a visited cell
                    if newRow * WIDTH + newCol in visited:
                        continue
                    # cannot go to a cell with a bigger difference
                    if abs(heights[newRow][newCol] - heights[r][c]) > effort:
                        continue
                    if dfs(newRow, newCol):
                        return True
                return False
            return dfs(0, 0)

        l = 0
        r = 10**6
        while l <= r:
            m = (r + l) // 2 # m is the max difference we try
            # if we can do it with this effort, try even less effort
            if canCrossPathWithinEffort(m):
                r = m - 1
            else:
                l = m + 1
        return r + 1
