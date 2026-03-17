class Solution:
    def projectionArea(self, grid: List[List[int]]) -> int:
        A = sum(
            grid[r][c] != 0 for r in range(len(grid)) for c in range(len(grid[0]))
        )
        B = sum(
            max(row) for row in grid
        )
        C = 0
        for c in range(len(grid[0])):
            big = 0
            for r in range(len(grid)):
                big = max(big, grid[r][c])
            C += big
        return A + B + C