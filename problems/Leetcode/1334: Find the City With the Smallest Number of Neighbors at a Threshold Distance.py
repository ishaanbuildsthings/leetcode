# https://leetcode.com/problems/find-the-city-with-the-smallest-number-of-neighbors-at-a-threshold-distance/description/
# difficulty: medium
# tags: graph, floyd warshall, djikstra

# Problem
# There are n cities numbered from 0 to n-1. Given the array edges where edges[i] = [fromi, toi, weighti] represents a bidirectional and weighted edge between cities fromi and toi, and given the integer distanceThreshold.

# Return the city with the smallest number of cities that are reachable through some path and whose distance is at most distanceThreshold, If there are multiple such cities, return the city with the greatest number.

# Notice that the distance of a path connecting cities i and j is equal to the sum of the edges' weights along that path.

# Solution, O(n^3) time and space. Just do a floyd warshall.
# * Solution 2, we can also do djikstra starting from each possible node

class Solution:
    def findTheCity(self, n: int, edges: List[List[int]], distanceThreshold: int) -> int:
        edgeMap = defaultdict(lambda: defaultdict(lambda: float('inf')))
        for a, b, w in edges:
            edgeMap[a][b] = w
            edgeMap[b][a] = w

        dist = [[float('inf')] * n for _ in range(n)] # dist from i to j
        for i in range(n):
            for j in range(n):
                if i == j:
                    dist[i][j] = 0
                    continue
                dist[i][j] = edgeMap[i][j] # add edges if they exist

        for k in range(n):
            for i in range(n):
                for j in range(n):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

        res = None
        resCount = float('inf')
        for i in range(n):
            reach = 0
            for j in range(n):
                if dist[i][j] <= distanceThreshold:
                    reach += 1
            if reach <= resCount:
                resCount = reach
                res = i
        return res



