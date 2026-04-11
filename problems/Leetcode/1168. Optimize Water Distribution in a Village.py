class Solution:
    def minCostToSupplyWater(self, n: int, wells: List[int], pipes: List[List[int]]) -> int:
        for i in range(len(pipes)):
            pipes[i][0] -= 1
            pipes[i][1] -= 1
        adj = defaultdict(list)
        for a, b, c in pipes:
            adj[a].append((b, c))
            adj[b].append((a, c))

        heap = [(x, i) for i, x in enumerate((wells))] # heap is going to hold (value, node), don't need to distinguish between pipe or well
        heapq.heapify(heap)

        res = 0
        seen = set()
        while len(seen) < n:
            while heap:
                smallest, node = heapq.heappop(heap)
                if node in seen:
                    continue
                break
            res += smallest
            seen.add(node)
            for outgoing, cost in adj[node]:
                heapq.heappush(heap, (cost, outgoing))

        return res
