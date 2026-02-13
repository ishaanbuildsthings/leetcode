class Solution:
    def maxIncreaseKeepingSkyline(self, grid: List[List[int]]) -> int:
        rmax = defaultdict(int)
        cmax = defaultdict(int)
        h = len(grid)
        w = len(grid[0])
        for r in range(h):
            for c in range(w):
                rmax[r] = max(rmax[r], grid[r][c])
                cmax[c] = max(cmax[c], grid[r][c])
        res = 0
        for r in range(h):
            for c in range(w):
                res += min(rmax[r], cmax[c]) - grid[r][c]
        
        return res