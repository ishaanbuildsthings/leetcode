class Solution:
    def maxPathScore(self, grid: List[List[int]], k: int) -> int:

        costMap = {
            0 : 0,
            1 : 1,
            2 : 1
        }

        h = len(grid)
        w = len(grid[0])
        @cache
        def dp(r, c, cost):
            if cost > k:
                return -inf
            if r == h or c == w:
                return -inf
            if r == h - 1 and c == w - 1:
                return 0
            down = dp(r + 1, c, cost + costMap[grid[r + 1][c]]) + grid[r + 1][c] if r + 1 < h else -inf

            right = dp(r, c + 1, cost + costMap[grid[r][c + 1]]) + grid[r][c + 1] if c + 1 < w else -inf
            return max(down, right)
        
        ans = dp(0, 0, costMap[grid[0][0]]) + grid[0][0]
        dp.cache_clear()
        if ans == -inf:
            return -1
        return ans

            