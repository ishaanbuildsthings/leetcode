class Solution:
    def minTimeMaxPower(self, n: int, edges: List[List[int]], power: int, cost: List[int], source: int, target: int) -> List[int]:
        INF = 10**18

        minD = [[INF] * (power + 1) for _ in range(n)]
        # minD[node][power] is the min time to reach that node with this much power

        adj = [[] for _ in range(n)]
        for a, b, t in edges:
            adj[a].append((b, t))


        heap = [(0, source, power)] # holds (time, node, power)
        minD[source][power] = 0

        while heap:
            time, node, p = heapq.heappop(heap)
            if minD[node][p] != time:
                continue
                
            for adjN, adjT in adj[node]:
                c = cost[node]
                if c > p:
                    continue
                newPower = p - c
                ntime = time + adjT

                if minD[adjN][newPower] <= ntime:
                    continue
                minD[adjN][newPower] = ntime
                heapq.heappush(heap, (ntime, adjN, newPower))

        resTime = INF
        resPower = -INF
        for p in range(power + 1):
            minTime = minD[target][p]
            if minTime < resTime:
                resTime = minTime
                resPower = p
            elif minTime == resTime:
                resPower = max(resPower, p)

        if resTime >= INF:
            return [-1, -1]

        return [resTime, resPower]
            
        