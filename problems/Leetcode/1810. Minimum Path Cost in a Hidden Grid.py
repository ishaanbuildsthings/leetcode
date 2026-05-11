# """
# This is GridMaster's API interface.
# You should not implement it, or speculate about its implementation
# """
#class GridMaster(object):
#    def canMove(self, direction: str) -> bool:
#        
#
#    def move(self, direction: str) -> int:
#        
#
#    def isTarget(self) -> bool:
#        
#

MOVE_MAP = {
    'R' : (0, 1),
    'D' : (1, 0),
    'L' : (0, -1),
    'U' : (-1, 0)
}

INV = {
    'R' : 'L',
    'L' : 'R',
    'U' : 'D',
    'D' : 'U'
}

class Solution(object):
    def findShortestPath(self, master: 'GridMaster') -> int:        
        adj = defaultdict(list) # (r, c) -> [(r, c, w), (r, c, w), ...]

        seen = set() # holds (r, c)

        target = None

        def dfs(r, c):
            nonlocal target
            if master.isTarget():
                target = (r, c)
            seen.add((r, c))
            for move in MOVE_MAP:
                if not master.canMove(move):
                    continue
                tup = MOVE_MAP[move]
                nr = r + tup[0]
                nc = c + tup[1]

                w = master.move(move)
                adj[(r, c)].append((nr, nc, w))
                master.move(INV[move])

                if (nr, nc) in seen:
                    continue
                
                master.move(move)
                dfs(nr, nc)
                master.move(INV[move])
        
        dfs(0, 0)


        if target is None:
            return -1

        heap = [(0, 0, 0)] # holds (cost, r, c)
        minD = defaultdict(lambda: inf)
        while heap:
            cost, r, c = heapq.heappop(heap)
            if minD[(r, c)] <= cost:
                continue
            minD[(r, c)] = cost

            for adjR, adjC, adjW in adj[(r, c)]:
                ncost = cost + adjW
                if minD[(adjR, adjC)] <= ncost: continue
                heapq.heappush(heap, (ncost, adjR, adjC))
        
        return minD[(target[0], target[1])]