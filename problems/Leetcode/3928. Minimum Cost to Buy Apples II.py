class Solution:
    def minCost(self, n: int, prices: List[int], roads: List[List[int]]) -> List[int]:

        # phase 1, go from any node to all other nodes

        distances = [None] * n # maps node -> dist map

        adj = defaultdict(list)
        for a, b, cost, tax in roads:
            adj[a].append((b,cost))
            adj[b].append((a,cost))

        def getDist(src):
            minD = [inf] * n

            heap = [(0, src)] # holds (cost, node)

            while heap:
                cost, node = heapq.heappop(heap)
                if minD[node] <= cost:
                    continue
                minD[node] = cost
                for adjN, adjW in adj[node]:
                    ncost = cost + adjW
                    if minD[adjN] <= ncost:
                        continue
                    heapq.heappush(heap, (ncost, adjN))

            return minD

        for node in range(n):
            distmap = getDist(node)
            # print(f'{distmap=}')
            distances[node] = distmap


        adj2 = defaultdict(list)
        for a, b, cost, tax in roads:
            adj2[a].append((b,cost*tax))
            adj2[b].append((a,cost*tax))

        def taxed(src):
            minD = [inf] * n

            heap = [(0, src)] # holds (cost, node)

            while heap:
                cost, node = heapq.heappop(heap)
                if minD[node] <= cost:
                    continue
                minD[node] = cost
                for adjN, adjW in adj2[node]:
                    ncost = cost + adjW
                    if minD[adjN] <= ncost:
                        continue
                    heapq.heappush(heap, (ncost, adjN))

            return minD

        mirror = [None] * n
        for node in range(n):
            distmap = taxed(node)
            # print(f'{distmap=}')
            mirror[node] = distmap

        res = []
        for node in range(n):
            best = inf
            for node2 in range(n):
                travel1 = distances[node][node2]
                apple = prices[node2]
                travel2 = mirror[node2][node]
                best = min(best, travel1 + apple + travel2)
            res.append(best)

        return res
                
            
        
            