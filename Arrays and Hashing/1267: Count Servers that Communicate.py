# https://leetcode.com/problems/count-servers-that-communicate/description/
# difficulty: medium

# problem
# You are given a map of a server center, represented as a m * n integer matrix grid, where 1 means that on that cell there is a server and 0 means that it is no server. Two servers are said to communicate if they are on the same row or on the same column.

# Return the number of servers that communicate with any other server.

# Solution, O(m*n) time and space, just count and add

class Solution:
    def countServers(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        seen = set()

        rowSums = {} # maps a row to how many servers it has
        for i, row in enumerate(grid):
            rowSums[i] = sum(row)

        colSums = defaultdict(int)
        for c in range(WIDTH):
            for r in range(HEIGHT):
                if grid[r][c] == 1:
                    colSums[c] += 1

        for r in range(HEIGHT):
            for c in range(WIDTH):
                if grid[r][c] == 1 and (rowSums[r] > 1 or colSums[c] > 1):
                    seen.add(r * WIDTH + c)
        return len(seen)




