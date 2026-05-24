class Solution:
    def cherryPickup(self, grid: List[List[int]]) -> int:
        height = len(grid)
        width = len(grid[0])

        # n^3 even though it looks n^4

        @cache
        def dp(r1, c1, r2, c2):
            if r1 == height - 1 and c1 == width - 1:
                return grid[-1][-1]
            resHere = 0
            resHere += grid[r1][c1]
            if r2 != r1 or c2 != c1:
                resHere += grid[r2][c2]
            
            opt = -inf
            for firstDir in [[1,0],[0,1]]:
                for secondDir in [[1,0],[0,1]]:
                    nr1 = r1 + firstDir[0]
                    nc1 = c1 + firstDir[1]
                    nr2 = r2 + secondDir[0]
                    nc2 = c2 + secondDir[1]
                    if nr1 < 0 or nc1 < 0 or nr2 < 0 or nc2 < 0 or nr1 == height or nc1 == width or nr2 == height or nc2 == width:
                        continue
                    if grid[nr1][nc1] == -1:
                        continue
                    if grid[nr2][nc2] == -1:
                        continue
                    opt = max(opt, dp(nr1,nc1,nr2,nc2))
            return resHere + opt
        
        a = dp(0,0,0,0)
        if a == -inf:
            return 0
        return a
                    