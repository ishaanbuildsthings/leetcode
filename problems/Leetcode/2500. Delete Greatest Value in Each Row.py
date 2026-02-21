class Solution:
    def deleteGreatestValue(self, grid: List[List[int]]) -> int:
        res = 0
        for row in grid:
            row.sort()
        for i in range(len(grid[0])):
            mx = -inf
            for j in range(len(grid)):
                mx = max(mx, grid[j][i])
            res += mx
        return res

        