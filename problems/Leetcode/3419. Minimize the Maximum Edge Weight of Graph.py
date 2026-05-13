# SOLUTION 1, BINARY SEARCH
class Solution:
    def minMaxWeight(self, n: int, edges: List[List[int]], threshold: int) -> int:

        def canKeepLte(x):
            adjRev = defaultdict(list)
            for a, b, w in edges:
                if w > x:
                    continue
                adjRev[b].append(a)
            
            seen = set() # holds nodes
            def dfs(node):
                seen.add(node)
                for adjN in adjRev[node]:
                    if adjN in seen: continue
                    dfs(adjN)
            dfs(0)
            return len(seen) == n

        l = 1
        r = 10**6 
        res = None
        while l <= r:
            m = (l + r) // 2
            if canKeepLte(m):
                res = m
                r = m - 1
            else:
                l = m + 1
        
        if res is None:
            return -1
        
        return res


# SOLUTION 2, CLEVER DIJKSTRA
class Solution:
    def minMaxWeight(self, n: int, edges: List[List[int]], threshold: int) -> int:
        edges.sort(key=lambda x: x[2])
        revAdj = [[] for _ in range(n)] # ToNode -> FromNode, Weight
        
        for a, b, w in edges:
            revAdj[b].append((a, w))
            
        INF = 10**15
        dist = [INF] * n
        dist[0] = 0
        h = [(0, 0)]
        
        while h:
            c, u = heapq.heappop(h)
            if c > dist[u]:
                continue
            for v, w in revAdj[u]:
                cost = max(c, w)
                if cost < dist[v]:
                    dist[v] = cost
                    heapq.heappush(h, (cost, v))
                    
        if any(d == INF for d in dist):
            return -1
        return max(dist)