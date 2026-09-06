class Solution:
    def minCost(self, grid: list[list[int]], k: int) -> int:
        height = len(grid)
        width = len(grid[0])

        # (cost, r, c, turnsUsed, lastDir)

        DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
        DIRtoI = {
            -1:0,
            (1,0):1,
            (-1,0):2,
            (0,1):3,
            (0,-1):4
        }

        # 75 x 75 x 75 x 4 = 1e6 ish

        S = (height * width * (k + 1) * 5)
        minD = [inf] * S

        def key(r, c, turnsUsed, lastDir):
            return (
                r * (width * (k + 1) * 5)
            ) + (
                c * (k + 1) * 5
            ) + (
                turnsUsed * 5
            ) + DIRtoI[lastDir]
            # return 
            # ans = 0
            # ans += r * (width * (k + 1) * 5)
            # ans += c * (k + 1) * 5
            # ans += turnsUsed * 5
            # ans += DIRtoI[lastDir]
            # return ans

        minD = defaultdict(lambda : inf)
        heap = []
        heap.append((grid[0][0], 0, 0, 0, -1))
        minD[key(0,0,0,-1)] = grid[0][0]
        # minD[0, 0, 0, -1] = grid[0][0]
        while heap:
            cost, r, c, turnsUsed, lastDir = heapq.heappop(heap)
            keySpot = key(r,c,turnsUsed,lastDir)
            if cost != minD[keySpot]:
            # if cost != minD[r, c, turnsUsed, lastDir]:
                continue
            for dr, dc in DIRS:
                nr = r + dr
                nc = c + dc
                if nr >= height or nr < 0 or nc >= width or nc < 0:
                    continue

                nturns = turnsUsed
                if (dr, dc) != lastDir:
                    nturns += 1
                if lastDir == -1:
                    nturns = 0
                if nturns > k:
                    continue
                ncost = cost + grid[nr][nc]
                # if minD[nr, nc, nturns, (dr, dc)] <= ncost:
                nkeySpot = key(nr,nc,nturns,(dr, dc))
                if minD[nkeySpot] <= ncost:
                    continue
                # minD[nr, nc, nturns, (dr, dc)] = ncost
                minD[nkeySpot] = ncost
                heapq.heappush(heap, (ncost, nr, nc, nturns, (dr, dc)))
                # print(f'appended: {ncost=} {nr=} {nc=} {nturns=}')

        res = inf
        for turns in range(k + 1):
            for lastDir in [(1,0),(-1,0),(0,1),(0,-1),-1]:
                keySpot = key(height-1,width-1,turns,lastDir)
                res = min(res, minD[keySpot])
                # res = min(res, minD[height - 1, width - 1, turns, lastDir])

        if res == inf:
            return -1

        return res
            