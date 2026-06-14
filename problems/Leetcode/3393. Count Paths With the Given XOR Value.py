class Solution:
    def countPathsWithXorValue(self, grid: List[List[int]], k: int) -> int:
        height = len(grid)
        width = len(grid[0])
        
        MOD = 10**9 + 7
        @cache
        def dp(r, c, currXor):
            if r == height - 1 and c == width - 1:
                return 1 if currXor == k else 0
            
            resHere = 0
            # can move down
            if r < height - 1:
                moveDown = dp(r + 1, c, currXor ^ grid[r + 1][c])
                resHere += moveDown
            
            # move right
            if c < width - 1:
                moveRight = dp(r, c + 1, currXor ^ grid[r][c + 1])
                resHere += moveRight
            
            return resHere % MOD
        
        a = dp(0, 0, grid[0][0])
        dp.cache_clear()
        return a
            