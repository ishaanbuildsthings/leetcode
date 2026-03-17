class Solution:
    def shortestPathWithHops(self, n: int, edges: List[List[int]], s: int, d: int, k: int) -> int:
        adjMap = defaultdict(lambda: defaultdict(lambda: inf))
        for a, b, w in edges:
            adjMap[a][b] = w
            adjMap[b][a] = w
        
        heap = []
        heap.append((0, s, 0)) # curr dist, curr node, skips used
        nodeAndDistToMinSkips = defaultdict(lambda: inf) # maps (node, dist) -> min skips used, for pruning
        minDists = defaultdict(lambda: inf) # maps (currNode, skipsUsed) -> min dist, holds only POPPED values
        while heap:
            currDist, currNode, skipsUsed = heapq.heappop(heap)
            if (currNode, skipsUsed) in minDists:
                continue
            if nodeAndDistToMinSkips[(currNode, currDist)] <= skipsUsed:
                continue
            # prune trick but doesn't seem to affect run time
            nodeAndDistToMinSkips[(currNode, currDist)] = skipsUsed
            minDists[(currNode, skipsUsed)] = currDist
            for adj in adjMap[currNode]:
                adjW = adjMap[currNode][adj]
                newW = currDist + adjW

                heapq.heappush(heap, (newW, adj, skipsUsed)) # no skip
                if skipsUsed < k:
                    heapq.heappush(heap, (currDist, adj, skipsUsed + 1))
        
        res = inf
        for skipUse in range(k + 1):
            res = min(res, minDists[(d, skipUse)])
        return res