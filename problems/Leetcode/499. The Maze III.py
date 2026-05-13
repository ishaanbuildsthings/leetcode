class Solution:
    def findShortestWay(self, maze: List[List[int]], ball: List[int], hole: List[int]) -> str:
        height = len(maze)
        width = len(maze[0])

        # computes the stop index an distance and if we pass over the hole
        @cache
        def dp(r, c, dirTup):
            nr, nc = r + dirTup[0], c + dirTup[1]
            # would hit a border next
            if nr < 0 or nr == height or nc < 0 or nc == width:
                return (r, c)
            if maze[nr][nc] == 1:
                return (r, c)
            # we hit the hole
            if r == hole[0] and c == hole[1]:
                return (r, c)
            return dp(nr, nc, dirTup)
        
        lToDirTup = {
            'd' : (1, 0),
            'l' : (0, -1),
            'r' : (0, 1),
            'u' : (-1, 0)
        }

        def getDist(p1, p2):
            return abs(p1[0]-p2[0]) + abs(p1[1]-p2[1])
        
        heap = [(0, '', ball[0], ball[1])] # hold (dist, path, r, c)
        minD = defaultdict(lambda : inf) # map (r, c) -> min dist
        while heap:
            dist, path, r, c = heapq.heappop(heap)
            if minD[(r, c)] <= dist:
                continue
            minD[(r, c)] = dist
            if r == hole[0] and c == hole[1]:
                return path
            for dir in lToDirTup:
                tup = lToDirTup[dir]
                npath = path + dir
                nextPos = dp(r, c, tup)
                ncost = dist + getDist((r, c), nextPos)
                if minD[(nextPos[0], nextPos[1])] <= ncost:
                    continue
                heapq.heappush(heap, (ncost, npath, nextPos[0], nextPos[1]))
        
        return 'impossible'