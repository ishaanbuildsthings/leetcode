class Solution:
    def surfaceArea(self, grid: List[List[int]]) -> int:
        res = 0
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                res += 2 if grid[r][c] else 0 # add top and bottom
                aboveHeight = grid[r - 1][c] if r > 0 else 0
                # if the above height is lower than ours, add it
                if aboveHeight < grid[r][c]:
                    res += grid[r][c] - aboveHeight
                
                belowHeight = grid[r + 1][c] if r < len(grid) - 1 else 0
                if belowHeight < grid[r][c]:
                    res += grid[r][c] - belowHeight
                
                leftHeight = grid[r][c-1] if c > 0 else 0
                if leftHeight < grid[r][c]:
                    res += grid[r][c] - leftHeight
                
                rightHeight = grid[r][c+1] if c < len(grid[0]) - 1 else 0
                if rightHeight < grid[r][c]:
                    res += grid[r][c] - rightHeight
                
                print(f'res: {res} after: {grid[r][c]}')
        
        return res