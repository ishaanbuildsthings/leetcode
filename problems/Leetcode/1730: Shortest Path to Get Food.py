# https://leetcode.com/problems/shortest-path-to-get-food/description/
# difficulty: medium
# tags: bfs

# Problem
# You are starving and you want to eat food as quickly as possible. You want to find the shortest path to arrive at any food cell.

# You are given an m x n character matrix, grid, of these different types of cells:

# '*' is your location. There is exactly one '*' cell.
# '#' is a food cell. There may be multiple food cells.
# 'O' is free space, and you can travel through these cells.
# 'X' is an obstacle, and you cannot travel through these cells.
# You can travel to any adjacent cell north, east, south, or west of your current location if there is not an obstacle.

# Return the length of the shortest path for you to reach any food cell. If there is no path for you to reach food, return -1.

# Solution, standard bfs
class Solution:
    def getFood(self, grid: List[List[str]]) -> int:
        height = len(grid)
        width = len(grid[0])

        q = collections.deque()

        for r in range(height):
            for c in range(width):
                if grid[r][c] == '*':
                    startR = r
                    startC = c
                    break

        q.append((startR, startC))
        seen = {(startR, startC)}
        steps = 0

        DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]

        while q:
            steps += 1
            length = len(q)
            for _ in range(length):
                r, c = q.popleft()
                for rowDiff, colDiff in DIFFS:
                    newRow = r + rowDiff
                    newCol = c + colDiff
                    if newRow < 0 or newRow == height or newCol < 0 or newCol == width or (newRow, newCol) in seen or grid[newRow][newCol] == 'X':
                        continue
                    if grid[newRow][newCol] == '#':
                        return steps
                    seen.add((newRow, newCol))
                    q.append((newRow, newCol))
        return -1


