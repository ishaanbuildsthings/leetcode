class Solution:
    def countPyramids(self, grid: List[List[int]]) -> int:
        h = len(grid)
        w = len(grid[0])

        flipped = [grid[r] for r in range(h - 1, -1, -1)]

        # gets the biggest with peak at (r, c)
        @cache
        def dp(r, c, op):
            supply = grid if op else flipped
            if not supply[r][c]:
                return 0
            if r < h - 1 and c > 0 and c < w - 1 and supply[r+1][c] and supply[r+1][c-1] and supply[r+1][c + 1]:
                dl = dp(r + 1, c - 1, op)
                dr = dp(r + 1, c + 1, op)
                tight = min(dl, dr)
                return 1 + tight
            else:
                return 0
        
        res = 0
        for r in range(h):
            for c in range(w):
                sz = dp(r, c, 0)
                # flip matrix
                sz2 = dp(r, c, 1)
                res += sz
                res += sz2
                
        return res