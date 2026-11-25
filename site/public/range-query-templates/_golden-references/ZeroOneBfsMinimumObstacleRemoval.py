# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/ZeroOneBfsMinimumObstacleRemoval.py
# 0-1 BFS as a full solution to LeetCode 2290 "Minimum Obstacle Removal to Reach Corner"
# (https://leetcode.com/problems/minimum-obstacle-removal-to-reach-corner/).
# Dijkstra where every edge costs 0 or 1, with a deque instead of a heap: a 0-cost move goes to the front, a 1-cost move to the back,
# so the deque always holds distances d and d + 1 in sorted order. Relax on push (write the better distance right away), skip stale
# entries on pop. Locking a cell the first time it's seen happens to work here (the cost belongs to the cell entered), but not in general.
# Time O(V + E), space O(V).
from collections import deque
from math import inf
from typing import List

class Solution:
    def minimumObstacles(self, grid: List[List[int]]) -> int:
        HEIGHT = len(grid)
        WIDTH = len(grid[0])

        q = deque()
        minToReach = [[inf for _ in range(WIDTH)] for _ in range(HEIGHT)]
        q.append((0, 0, 0)) # holds (r, c, minToReachHere)

        while q:
            r, c, minToReachHere = q.popleft()
            # stale
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
