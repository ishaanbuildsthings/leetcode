class Solution:
    def removeOnes(self, inputGrid: List[List[int]]) -> int:
        H = len(inputGrid)
        W = len(inputGrid[0])
        
        def bt(grid, r, c):
            if r == H:
                if sum(grid[a][b] > 0 for a in range(H) for b in range(W)):
                    return inf
                return 0
            if grid[r][c] == 0:
                c += 1
                if c == W:
                    c = 0
                    r += 1
                return bt(grid, r, c)
            
            # if we skip this
            nc = c + 1
            if nc == W:
                nc = 0
                nr = r + 1
            else:
                nr = r
            ifSkip = bt(grid, nr, nc)

            updated = [] # holds cells we turned into 0, and need to undo
            # if we clear this
            for rr in range(H):
                if grid[rr][c] == 1:
                    grid[rr][c] = 0
                    updated.append([rr, c])
            for cc in range(W):
                if grid[r][cc] == 1:
                    grid[r][cc] = 0
                    updated.append([r, cc])
            
            ifClear = 1 + bt(grid, nr, nc)
            for rr, cc in updated:
                grid[rr][cc] = 1
            
            return min(ifClear, ifSkip)
        
        return bt(inputGrid, 0, 0)
        

            