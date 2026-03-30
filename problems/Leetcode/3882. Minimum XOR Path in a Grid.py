class Solution:
    def minCost(self, grid: list[list[int]]) -> int:
        height = len(grid)
        width = len(grid[0])
        @cache
        def dp(r, c, xor):
            if r == height - 1 and (c == width - 1):
                return xor ^ grid[r][c]

            if (r + 1) < height:
                down = dp(r + 1, c, xor ^ grid[r][c])
            else:
                down = inf

            if (c + 1) < width:
                right = dp(r, c + 1, xor ^ grid[r][c])
            else:
                right = inf

            return min(down, right)

        ans = dp(0,0,0)
        dp.cache_clear()
        return ans