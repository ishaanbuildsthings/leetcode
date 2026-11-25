class Solution:
    def minimumObstacles(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        q = deque()
        minToReach = [[inf for _ in range(WIDTH)] for _ in range(HEIGHT)]
        q.append((0, 0, 0)) # holds (r, c, minToReachHere)

        while q:
            r, c, minToReachHere = q.popleft()
            # state
            if minToReachHere > minToReach[r][c]:
                continue
            minToReach[r][c] = minToReachHere
            for rd, cd in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rd
                nc = c + cd
                if nr < 0 or nr == HEIGHT or nc < 0 or nc == WIDTH:
                    continue
                nd = minToReachHere + grid[nr][nc]
                if minToReach[nr][nc] <= nd:
                    continue
                minToReach[nr][nc] = nd
                if grid[nr][nc]:
                    q.append((nr, nc, nd))
                else:
                    q.appendleft((nr, nc, nd))
        
        return minToReach[-1][-1]
