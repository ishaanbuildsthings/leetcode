class Solution:
    def numberOfPaths(self, grid: List[List[int]], k: int) -> int:
        height = len(grid)
        width = len(grid[0])
        MOD = 10**9 + 7
        @cache
        def dp(r, c, remain):
            remain += grid[r][c]
            remain %= k
            if r == height - 1 and c == width - 1:
                return int(remain == 0)
            if r >= height or c >= width:
                return 0
            res = 0
            if r < height - 1:
                down = dp(r + 1, c, remain)
                res += down
            if c < width - 1:
                right = dp(r, c + 1, remain)
                res += right
            return res % MOD
        
        a = dp(0,0,0)
        dp.cache_clear()
        return a
