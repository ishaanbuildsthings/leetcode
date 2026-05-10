class Solution:
    def reachableNodes(self, edges: List[List[int]], maxMoves: int, n: int) -> int:
        minDists = defaultdict(lambda: inf) # minimum distance to reach this node

        maxConsumed = defaultdict(int) # maps (node, neighbor) to the max nodes consumed that direction

        heap = [(0, 0)] # holds dist, node

        adjMap = defaultdict(lambda: defaultdict(lambda: 1)) # maps a node to the "weight", a 1 means no division, a 2 means a single division, etc

        for a, b, cnt in edges:
            adjMap[a][b] = cnt + 1
            adjMap[b][a] = cnt + 1
        
        while heap:
            dist, node = heapq.heappop(heap)
            if dist >= minDists[node]:
                continue
            minDists[node] = dist

            for adj in adjMap[node]:
                weight = adjMap[node][adj]
                newWeight = weight + dist
                # if we can reach the node straight up
                if newWeight <= maxMoves:
                    maxConsumed[(node, adj)] = weight - 1
                    # extra prune
                    if newWeight >= minDists[adj]:
                        continue
                    heapq.heappush(heap, (newWeight, adj))
                    continue
                
                # if we cannot reach the node
                stepsAllowed = maxMoves - dist
                maxConsumed[(node, adj)] = max(maxConsumed[(node, adj)], stepsAllowed)
        
        res = 0

        # get counts of all normal nodes we can reach
        for node in range(n):
            if minDists[node] != inf:
                res += 1

        for a, b, cnt in edges:
            aToB = maxConsumed[(a, b)]
            bToA = maxConsumed[(b, a)]
            if aToB + bToA <= cnt:
                res += aToB + bToA
            else:
                res += cnt
        
        return res
        
