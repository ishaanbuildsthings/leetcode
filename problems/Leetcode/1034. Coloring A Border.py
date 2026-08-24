class Solution:
    def colorBorder(self, grid: List[List[int]], row: int, col: int, color: int) -> List[List[int]]:
        inComponent = set()

        def dfs(r, c):
            inComponent.add((r, c))
            for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                nR, nC = r+rowDiff, c+colDiff
                if (nR,nC) in inComponent:
                    continue
                if nR < 0 or nR == len(grid) or nC < 0 or nC == len(grid[0]):
                    continue
                if grid[nR][nC] != grid[row][col]:
                    continue
                dfs(nR, nC)
        dfs(row, col)

        changed = set()
        
        for r, c in inComponent:
            if r == 0 or r == len(grid) - 1 or c == 0 or c == len(grid[0]) - 1:
                changed.add((r, c))
                continue
            breaker = False
            for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                if breaker:
                    break
                nR, nC = r+rowDiff, c+colDiff
                if grid[nR][nC] != grid[r][c]:
                    changed.add((r,c))
                    breaker = True
        for r, c in changed:
            grid[r][c] = color
        return grid