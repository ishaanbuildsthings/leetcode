# """
# This is GridMaster's API interface.
# You should not implement it, or speculate about its implementation
# """
#class GridMaster(object):
#    def canMove(self, direction: str) -> bool:
#        
#
#    def move(self, direction: str) -> None:
#        
#
#    def isTarget(self) -> bool:
#        
#

class Solution(object):
    def findShortestPath(self, master: 'GridMaster') -> int:
        seen = {(0, 0)}
        target = None
        def dfs(r, c):
            nonlocal target
            seen.add((r, c))
            if master.isTarget():
                target = (r, c)
            for d in ['R', 'L', 'U', 'D']:
                if not master.canMove(d):
                    continue
                dr = 1 if d == 'R' else -1 if d == 'L' else 0
                dc = 1 if d == 'U' else -1 if d == 'D' else 0
                nr = r + dr
                nc = c + dc
                if (nr, nc) in seen:
                    continue
                master.move(d)
                dfs(nr, nc)
                opposite = {'R' : 'L', 'L' : 'R', 'U' : 'D', 'D' : 'U'}[d]
                master.move(opposite)
        dfs(0, 0)

        steps = 0
        q = deque()
        q.append((0, 0))
        seen2 = {(0, 0)}
        while q:
            length = len(q)
            for _ in range(length):
                r, c = q.popleft()
                if (r, c) == target:
                    return steps
                for dr, dc in [[1,0],[-1,0],[0,1],[0,-1]]:
                    nr = r + dr
                    nc = c + dc
                    if (nr, nc) not in seen:
                        continue
                    if (nr, nc) in seen2:
                        continue
                    q.append((nr, nc))
                    seen2.add((nr, nc))
            steps += 1
        
        return -1



