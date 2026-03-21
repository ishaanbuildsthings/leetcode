class Solution:
    def lenOfVDiagonal(self, grid: List[List[int]]) -> int:
        # maps a rowDiff, colDiff to its clockwise rotation diffs
        turning = {
            (1,1) : (1,-1),
            (1,-1): (-1,-1),
            (-1,-1): (-1,1),
            (-1,1): (1,1)
        }
        
        nextRequiredTile = { 2: 0, 0: 2, 1: 2 }
        
        height = len(grid)
        width = len(grid[0])
        
        @cache
        def dp(r, c, req, turnsMade, dirs):
            if r == height or r < 0 or c == width or c < 0:
                return 0
            if grid[r][c] != req:
                return 0
            
            rDiff, cDiff = dirs
            newReq = nextRequiredTile[req]
            
            # we must keep moving
            if turnsMade == 1:
                return 1 + dp(r+rDiff,c+cDiff,newReq, turnsMade, dirs)
            
            resHere = 1 + dp(r+rDiff,c+cDiff,newReq, turnsMade, dirs)
            tup = turning[dirs]
            rDiff, cDiff = tup
            nr = r+rDiff
            nc = c+cDiff
            ifWeTurnHere = dp(nr,nc,newReq,1,tup)
            return max(resHere, 1 + ifWeTurnHere)
            
            return resHere
                
        res = 0
        for r in range(height):
            for c in range(width):
                if grid[r][c] == 1:
                    dr = dp(r, c, 1, 0, (1,1))
                    ur = dp(r, c, 1, 0, (-1,1))
                    dl = dp(r, c, 1, 0, (1,-1))
                    ul = dp(r, c, 1, 0, (-1,-1))
                    res = max(res, dr, ur, dl, ul)
        dp.cache_clear()
        return res
            