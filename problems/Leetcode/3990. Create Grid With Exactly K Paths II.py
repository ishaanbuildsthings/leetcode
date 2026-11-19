class Solution:
    def createGrid(self, k: int) -> list[str]:
        SIDE = 25
        grid = [['#' for _ in range(SIDE)] for _ in range(SIDE)]
        for c in range(SIDE):
            grid[-1][c] = '.'

        for i in range(SIDE // 2):
            leftCol = 2 * i
            topRow = i
            grid[topRow][leftCol] = grid[topRow][leftCol+1] = grid[topRow+1][leftCol] = grid[topRow+1][leftCol+1] = '.'

        for b in range(15):
            if not k & (1 << b):
                continue
            leftCol = 2 * b
            topRow = b
            for r in range(topRow, SIDE):
                grid[r][leftCol] = '.'
        
        return grid