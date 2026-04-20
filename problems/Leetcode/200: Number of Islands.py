class Solution:
    def numIslands(self, grid: List[List[str]]) -> int:
        height = len(grid)
        width = len(grid[0])

        visited = set()
        res = 0
        def dfs(r, c):
            visited.add((r, c))
            for rowDiff, colDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                newRow, newCol = r + rowDiff, c + colDiff
                if newRow < 0 or newRow == height or newCol < 0 or newCol == width:
                    continue
                if grid[newRow][newCol] == '0':
                    continue
                if (newRow, newCol) in visited:
                    continue
                dfs(newRow, newCol)
        
        for r in range(height):
            for c in range(width):
                if grid[r][c] == '1' and not (r, c) in visited:
                    res += 1
                    dfs(r, c)
        
        return res
                
            