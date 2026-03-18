class Solution:
    def shortestPath(self, grid: List[List[int]], k: int) -> int:
        height = len(grid)
        width = len(grid[0])

        q = deque()
        q.append((0,0,0)) # holds r, c, breaks
        seen = set()
        seen.add((0,0,0))

        steps = 0
        while q:
            length = len(q)
            for _ in range(length):
                r, c, breaks = q.popleft()
                if r == height - 1 and c == width - 1:
                    return steps
                for rDiff, cDiff in [[1,0],[-1,0],[0,1],[0,-1]]:
                    nr, nc = r + rDiff, c + cDiff
                    if nr < 0 or nc < 0 or nr == height or nc == width:
                        continue
                    if grid[nr][nc] == 1:
                        newBreaks = breaks + 1
                        if newBreaks <= k:
                            newTup = (nr,nc,newBreaks)
                            if newTup not in seen:
                                seen.add(newTup)
                                q.append(newTup)
                    else:
                        newTup = (nr, nc, breaks)
                        if newTup not in seen:
                            seen.add(newTup)
                            q.append(newTup)
            steps += 1
        
        return -1



