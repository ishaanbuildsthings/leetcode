class Solution:
    def minimumOperations(self, grid: List[List[int]]) -> int:
        res = 0
        height = len(grid)
        width = len(grid[0])
        for c in range(width):
            for r in range(height - 1):
                below = grid[r + 1][c]
                if grid[r + 1][c] <= grid[r][c]:
                    newV = grid[r][c] + 1
                    oldV = grid[r + 1][c]
                    gained = newV - oldV
                    grid[r + 1][c] = newV
                    res += gained
        return res
                
                