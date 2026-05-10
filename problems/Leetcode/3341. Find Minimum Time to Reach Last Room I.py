class Solution:
    def minTimeToReach(self, moveTime: List[List[int]]) -> int:
        H = len(moveTime)
        W = len(moveTime[0])
        minTime = defaultdict(lambda : inf)
        heap = [(0, 0, 0)] # holds (time, r, c)
        while heap:
            time, r, c = heapq.heappop(heap)
            if minTime[(r, c)] <= time: continue
            minTime[(r, c)] = time
            for rdiff, cdiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                nr = r + rdiff
                nc = c + cdiff
                if nr < 0 or nr == H or nc < 0 or nc == W: continue
                ntime = max(time + 1, moveTime[nr][nc] + 1)
                if minTime[(nr, nc)] <= ntime: continue
                heapq.heappush(heap, (ntime, nr, nc))
        return minTime[(H - 1, W - 1)]