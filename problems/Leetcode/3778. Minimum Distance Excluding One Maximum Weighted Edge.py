class Solution:
    def minCostExcludingMax(self, n: int, edges: List[List[int]]) -> int:
        minD0 = defaultdict(lambda: inf) # node to minimum distance
        minD1 = defaultdict(lambda: inf)
        heap = [] # holds (node, used excluded edge, min distance)
        heap.append((0, 0, 0))
        g = [[] for _ in range(n)]
        for a, b, w in edges:
            g[a].append((b, w))
            g[b].append((a, w))
        while heap:
            node, usedExclusion, dist = heapq.heappop(heap)
            if usedExclusion == 0:
                if dist >= minD0[node]:
                    continue
                else:
                    minD0[node] = dist
            else:
                if dist >= minD1[node]:
                    continue
                else:
                    minD1[node] = dist
            for adjN, adjW in g[node]:
                # no skip
                noSkipDist = dist + adjW
                # prune
                if noSkipDist < (minD0[adjN] if not usedExclusion else minD1[adjN]):
                    heapq.heappush(heap, (adjN, usedExclusion, noSkipDist))
                if not usedExclusion:
                    # prune
                    if dist < minD1[adjN]:
                        heapq.heappush(heap, (adjN, 1, dist))
        return minD1[n - 1]
            
            