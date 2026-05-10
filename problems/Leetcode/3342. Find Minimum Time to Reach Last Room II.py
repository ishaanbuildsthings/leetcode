class Solution:
    def minTimeToReach(self, moveTime: List[List[int]]) -> int:
        H = len(moveTime)
        W = len(moveTime[0])
        minD = defaultdict(lambda : inf) # maps (r, c, parity) -> min time
        heap = [(0, 0, 0, 0)] # (time, r, c, parity)
        while heap:
            time, r, c, parity = heapq.heappop(heap)
            if minD[(r, c, parity)] <= time: continue
            minD[(r, c, parity)] = time
            for rdiff, cdiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rdiff
                nc = c + cdiff
                if nr < 0 or nr == H or nc < 0 or nc == W:
                    continue
                step = 1 if parity == 0 else 2
                ntime = max(time + step, moveTime[nr][nc] + step)
                if minD[(nr, nc, parity ^ 1)] <= ntime: continue
                heapq.heappush(heap, (ntime, nr, nc, parity ^ 1))
        return min(minD[(H - 1, W - 1, 0)], minD[(H - 1, W - 1, 1)])
