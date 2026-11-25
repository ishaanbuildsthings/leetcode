# https://leetcode.com/problems/shortest-bridge/description/
# Difficulty: Medium
# Tags: matrix dfs, matrix bfs

# Problem
# You are given an n x n binary matrix grid where 1 represents land and 0 represents water.

# An island is a 4-directionally connected group of 1's not connected to any other 1's. There are exactly two islands in grid.

# You may change 0's to 1's to connect the two islands to form one island.

# Return the smallest number of 0's you must flip to connect the two islands.

# Solution, O(n^2) time, O(n^2) space
# First, identify an island. We do this by iterating until we hit land, then, at that land cell only, dfs out and add all land cells to seen. Now seen contains just the first island. Then, we bfs for every land cell, until we reach the second island (a land cell not in seen). At most, each bfs cell is processed once, so the time is n^2 and space is n^2, if we use a real queue.

class Solution:
    def shortestBridge(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])
        diffs = [[1, 0], [-1, 0], [0, 1], [0, -1] ]

        seen = set() # will hold all coordinates of the first island

        def dfs(r, c):
            seen.add(r * WIDTH + c)

            for rowDiff, colDiff in diffs:
                newRow = rowDiff + r
                newCol = colDiff + c
                # skip out of bounds
                if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                    continue
                # skip water
                if grid[newRow][newCol] == 0:
                    continue
                # skip cells we have seen
                key = newRow * WIDTH + newCol
                if key in seen:
                    continue

                dfs(newRow, newCol)

        hasSeenFirstIsland = False
        for r in range(HEIGHT):
            if hasSeenFirstIsland:
                break
            for c in range(WIDTH):
                if grid[r][c] == 1:
                    dfs(r, c)
                    hasSeenFirstIsland = True
                    break

        # now all of the first island is in seen

        q = collections.deque()

        for hash in list(seen):
            r = hash // WIDTH
            c = hash - (r * WIDTH)
            q.append([r, c])


        result = -1 # if we can reach the other island in 2 jumps, then we need to flip one cell essentially
        while len(q):
            result += 1
            qLength = len(q)
            for i in range(qLength):
                r, c = q.popleft()
                # bfs out until we reach a cell with a 1 that isn't in seen
                for rowDiff, colDiff in diffs:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    key = newRow * WIDTH + newCol
                    # skip out of bounds
                    if newRow == HEIGHT or newRow < 0 or newCol == WIDTH or newCol < 0:
                        continue
                    # skip cells we have already seen
                    if key in seen:
                        continue
                    if grid[newRow][newCol] == 1:
                        return result
                    q.append([newRow, newCol])
                    seen.add(key) # prevent multiple cells in one iteration from adding an adj cell







