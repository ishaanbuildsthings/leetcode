class Solution:
    def shortestPath(self, n: int, edges: List[List[int]], labels: str, k: int) -> int:

        heap = [] # holds (dist, node, lastLetter, streak)
        heap.append((0, 0, labels[0], 1))

        adj = defaultdict(list) # adj[node] -> [(adjN, adjW), ...]
        for a, b, w in edges:
            adj[a].append((b, w))

        minD = defaultdict(lambda: inf) # minD[(node, letter, streak)] = min dist

        while heap:
            dist, node, lastLetter, streak = heapq.heappop(heap)
            if node == n - 1:
                return dist
            if minD[(node, lastLetter, streak)] <= dist:
                continue
            minD[(node, lastLetter, streak)] = dist
            for adjN, adjW in adj[node]:
                adjLetter = labels[adjN]
                nstreak = streak + 1 if lastLetter == adjLetter else 1
                if nstreak > k:
                    continue
                nd = dist + adjW
                if minD[(adjN, adjLetter, nstreak)] <= nd:
                    continue
                heapq.heappush(heap, (nd, adjN, adjLetter, nstreak))



        return -1
            