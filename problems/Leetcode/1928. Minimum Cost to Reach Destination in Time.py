class Solution:
    def minCost(self, maxTime: int, edges: List[List[int]], passingFees: List[int]) -> int:

        cities = set()
        for a, b, w in edges:
            cities.add(a)
            cities.add(b)
        n = len(cities)

        adj = [[] for _ in range(n)] # adj[node] -> [(adjN, w), ...]
        for a, b, w in edges:
            adj[a].append((b, w))
            adj[b].append((a, w))
        
        minD = [[inf] * (maxTime + 1) for _ in range(n)] # minD[node][time] -> min cost
        
        heap = [(passingFees[0], 0, 0)] # holds (cost, node, time)
        while heap:
            cost, node, time = heapq.heappop(heap)
            if minD[node][time] <= cost:
                continue
            minD[node][time] = cost
            if node == n - 1:
                return cost

            for adjN, adjTime in adj[node]:
                ntime = time + adjTime
                if ntime > maxTime:
                    continue
                ncost = cost + passingFees[adjN]
                if minD[adjN][ntime] <= ncost:
                    continue
                heapq.heappush(heap, (ncost, adjN, ntime))
        
        return -1