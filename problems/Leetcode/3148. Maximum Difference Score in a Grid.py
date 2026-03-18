class Solution:
    def maxScore(self, grid: List[List[int]]) -> int:
        height = len(grid)
        w = len(grid[0])


        # gets us the biggest number down and right of us
        @cache
        def dp(r, c):
            if r == height and c == w:
                return -inf
            res = -inf
            if c < w - 1:
                biggestRight = max(grid[r][c + 1], dp(r, c + 1))
                res = biggestRight
            if r < height - 1:
                biggestDown = max(grid[r + 1][c], dp(r + 1, c))
                res = max(res, biggestDown)
            return res
        
        ans = -inf
        for r in range(height):
            for c in range(w):
                biggestDr = dp(r, c)
                ans = max(ans, biggestDr - grid[r][c])
        return ans
