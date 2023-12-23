# https://leetcode.com/problems/minimum-obstacle-removal-to-reach-corner/
# difficulty: hard
# tags: bfs, graph, connected, undirected, weighted, djiikstra

# Problem
# You are given a 0-indexed 2D integer array grid of size m x n. Each cell has one of two values:

# 0 represents an empty cell,
# 1 represents an obstacle that may be removed.
# You can move up, down, left, or right from and to an empty cell.

# Return the minimum number of obstacles to remove so you can move from the upper left corner (0, 0) to the lower right corner (m - 1, n - 1).

# Solution, O(m*n) time and space
# We can do a BFS, reaching further and further while incrementing the amount of removals by 1, until we reach the target region. I did this by using a DFS function that explores whenever we hit an empty cell, as a helper function to the BFS. We could use djikstra's with edges of weight 0 and 1 as well, or a 0-1 djikstra where we just prepend the queue with 0-weighted edges to avoid the log complexity, much simpler and no need for the dfs function!

class Solution:
    def minimumObstacles(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        def key(r, c):
            return r * WIDTH + c

        def inBounds(r, c):
            return r < HEIGHT and r >= 0 and c < WIDTH and c >= 0

        q = collections.deque()

        DIFFS = [ [1, 0], [-1, 0], [0, 1], [0, -1] ]
        def mark(r, c, markSet, addToQ):
            markSet.add(key(r, c))
            if addToQ:
                q.append([r, c])
            for rowDiff, colDiff in DIFFS:
                newRow = rowDiff + r
                newCol = colDiff + c
                if inBounds(newRow, newCol) and grid[newRow][newCol] == 0 and not key(newRow, newCol) in markSet:
                    mark(newRow, newCol, markSet, addToQ)
        seen = set() # cells we have access to
        mark(0, 0, seen, True)
        target = set()
        mark(HEIGHT - 1, WIDTH - 1, target, False)
        res = 0

        while q:
            length = len(q)
            for _ in range(length):
                popped = q.popleft()
                r, c = popped
                for rowDiff, colDiff in DIFFS:
                    newRow = rowDiff + r
                    newCol = colDiff + c
                    if not inBounds(newRow, newCol):
                        continue
                    if key(newRow, newCol) in target:
                        return res
                    if key(newRow, newCol) in seen:
                        continue
                    mark(newRow, newCol, seen, True)

            res += 1

# 0011110001
# 0111111011
# 1101111010
# 0011110011
# 1010001110