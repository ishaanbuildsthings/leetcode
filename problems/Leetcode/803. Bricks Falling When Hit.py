class Solution:
    def hitBricks(self, grid: List[List[int]], hits: List[List[int]]) -> List[int]:
        H = len(grid)
        W = len(grid[0])
        hitSet = set()
        for r, c in hits:
            hitSet.add((r, c))
        stable = [[0] * W for _ in range(H)]
        for r in range(H):
            for c in range(W):
                if grid[r][c] and (r, c) not in hitSet:
                    stable[r][c] = 1
        
        trueStable = set()
        
        def findStable(r, c):
            trueStable.add((r, c))
            for rd, cd in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rd
                nc = c + cd
                if nr < 0 or nr == H or nc < 0 or nc == W:
                    continue
                if (nr, nc) in trueStable:
                    continue
                if not stable[nr][nc]:
                    continue
                findStable(nr, nc)
        
        for c in range(W):
            if stable[0][c]:
                findStable(0, c)
        
        for r in range(H):
            for c in range(W):
                if (r, c) in trueStable:
                    stable[r][c] = 1
                else:
                    stable[r][c] = 0
        
        res = [None] * len(hits)

        repaired = set()

        def dfs(r, c):
            gain = 1
            stable[r][c] = True
            for rd, cd in [[1,0],[0,1],[0,-1],[-1,0]]:
                nr = r + rd
                nc = c + cd
                if nr < 0 or nr == H or nc < 0 or nc == W:
                    continue
                # dont explore an already stable cell
                if stable[nr][nc]:
                    continue
                # dont explore a cell that never is a brick
                if not grid[nr][nc]:
                    continue
                # dont explore an upcoming stable cell if it hasnt been repaired
                if (nr, nc) in hitSet and (nr, nc) not in repaired:
                    continue
                gain += dfs(nr, nc)
            return gain

        for i in range(len(hits) - 1, -1, -1):
            r, c = hits[i]
            repaired.add((r, c))
            # if there was never a brick here
            if grid[r][c] == 0:
                res[i] = 0
                continue
            
            # as we loop backwards we are basically repairing bricks on the wall
            # if no adjacent brick to this was stable, after we knocked out this brick
            # then this brick couldn't have been stable, and thus would have already fallen
            stableAdj = 0
            for rd, cd in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rd
                nc = c + cd
                if nr < 0 or nr == H or nc < 0 or nc == W:
                    continue
                stableAdj += stable[nr][nc]
            if not stableAdj and r != 0:
                res[i] = 0 
                continue
            
            # at least one adjacent neighbor was stable after knocking out this brick, so this brick was connected
            gained = dfs(r, c)
            res[i] = gained - 1
        
        return res
                