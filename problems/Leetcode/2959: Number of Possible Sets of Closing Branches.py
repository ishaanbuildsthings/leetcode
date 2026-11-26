# https://leetcode.com/problems/number-of-possible-sets-of-closing-branches/description/
# difficulty: hard
# tags: graphs, floyd warshall, djikstra, bit mask, contest

# Problem
# There is a company with n branches across the country, some of which are connected by roads. Initially, all branches are reachable from each other by traveling some roads.

# The company has realized that they are spending an excessive amount of time traveling between their branches. As a result, they have decided to close down some of these branches (possibly none). However, they want to ensure that the remaining branches have a distance of at most maxDistance from each other.

# The distance between two branches is the minimum total traveled length needed to reach one branch from another.

# You are given integers n, maxDistance, and a 0-indexed 2D array roads, where roads[i] = [ui, vi, wi] represents the undirected road between branches ui and vi with length wi.

# Return the number of possible sets of closing branches, so that any branch has a distance of at most maxDistance from any other.

# Note that, after closing a branch, the company will no longer have access to any roads connected to it.

# Note that, multiple roads are allowed.


# Solution
# I used a bitmask to try all possible combinations then used floyd warshall. I also tried one where instead of floyd warshall, I did djikstra's from a node and got the shortest distance to all other nodes.

# the djikstra solution (floyd warshall is below, and what I did in contest)
class Solution:
    def numberOfSets(self, n: int, maxDistance: int, roads: List[List[int]]) -> int:
        _inner = lambda: defaultdict(lambda: float('inf'))
        edgeMap = defaultdict(_inner) # maps node to another node to the smallest edge weight

        for a, b, weight in roads:
            edgeMap[a][b] = min(edgeMap[a][b], weight)
            edgeMap[b][a] = min(edgeMap[b][a], weight)

        res = 0

        def isMaskDoable(mask):
            # pick a start node
            for startNode in range(n):
                bit = mask & (1 << startNode)
                # closed
                if bit:
                    continue
                totalOpen = sum(
                    0 if mask & (1 << offset) else
                    1
                    for offset in range(n)
                )

                # do djikstras to get max distance starting from source
                shortest = defaultdict(lambda: float('inf')) # shortest path from source to this node

                heap = [ [0, startNode] ] # holds distance, node
                maxDist = 0
                while heap:
                    dist, node = heapq.heappop(heap)
                    if dist > shortest[node]:
                        continue
                    shortest[node] = dist
                    maxDist = max(maxDist, dist)

                    for adj in edgeMap[node]:
                        # skip closed ones
                        if mask & (1 << adj):
                            continue
                        newDist = dist + edgeMap[node][adj]
                        # skip nodes we have better paths to
                        if shortest[adj] < newDist:
                            continue

                        heapq.heappush(heap, [newDist, adj])

                if maxDist > maxDistance:
                    return False
                if len(shortest) < totalOpen:
                    return False
            return True


        res = 0
        for mask in range(1 << n):
            res += isMaskDoable(mask)
        return res
# SECOND SOLUTION USING FLOYD WARSHALL
# class Solution:
#     def numberOfSets(self, n: int, maxDistance: int, roads: List[List[int]]) -> int:
#         _inner = lambda: defaultdict(lambda: float('inf'))
#         edgeMap = defaultdict(_inner) # maps node to another node to the smallest edge weight

#         for a, b, weight in roads:
#             edgeMap[a][b] = min(edgeMap[a][b], weight)
#             edgeMap[b][a] = min(edgeMap[b][a], weight)

#         # print(f'init edge map: {edgeMap}')

#         res = 0

#         def isMaskDoable(mask):
#             # FLOYD WARSHALL
#             distance = [[float('inf')] * n for _ in range(n)]

#             # populate with init distances
#             for i in range(n):
#                 # skip closed branches
#                 if mask & (1 << i):
#                     continue
#                 # set identity distance
#                 distance[i][i] = 0
#                 # iterate over adjacent nodes
#                 for j in edgeMap[i].keys():
#                     # skip adjacent closed ones
#                     if mask & (1 << j):
#                         continue
#                     # set initial edge
#                     distance[i][j] = edgeMap[i][j]

#             # allow us to use up to 0, 1, 2, ... k as our midpoint
#             for k in range(n):
#                 for i in range(n):
#                     for j in range(n):
#                         # if either is closed skip those, we cannot use them
#                         if mask & (1 << i) or mask & (1 << j):
#                             continue
#                         distance[i][j] = min(distance[i][j], distance[i][k] + distance[k][j])

#             # check every pair
#             for i in range(n):
#                 for j in range(n):
#                     if mask & (1 << i) or mask & (1 << j):
#                         continue
#                     if distance[i][j] > maxDistance:
#                         return False
#             return True

#         res = 0
#         for mask in range(1 << n):
#             res += isMaskDoable(mask)
#         return res


