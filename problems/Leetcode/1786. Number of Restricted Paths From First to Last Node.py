class Solution:
    def countRestrictedPaths(self, n: int, edges: List[List[int]]) -> int:
        adjMap = defaultdict(list)
        for a, b, w in edges:
            adjMap[a].append((b, w))
            adjMap[b].append((a, w))

        # compute min distance to all nodes, starting at n

        minDists = defaultdict(lambda: inf)
        heap = [(0, n)] # holds dist, node
        while heap:
            dist, node = heapq.heappop(heap)
            if dist >= minDists[node]:
                continue
            minDists[node] = dist
            for adj, w in adjMap[node]:
                if adj in minDists:
                    continue
                heapq.heappush(heap, (dist + w, adj))
        
        @cache
        def pathsToN(node):
            if node == n:
                return 1
            currDistFromLastNode = minDists[node]
            currWays = 0
            for adj, w in adjMap[node]:
                adjDistFromLastNode = minDists[adj]
                if adjDistFromLastNode >= currDistFromLastNode:
                    continue
                currWays += pathsToN(adj)
            return currWays
        
        return pathsToN(1) % (10**9 + 7)
