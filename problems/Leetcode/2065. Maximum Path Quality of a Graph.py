class Solution:
    def maximalPathQuality(self, values: List[int], edges: List[List[int]], maxTime: int) -> int:
        res = 0

        adj = defaultdict(lambda: defaultdict(int))
        for a, b, w in edges:
            adj[a][b] = w
            adj[b][a] = w
        
        def dfs(node, pathSet, pathSum, currTime):
            nonlocal res
            if currTime > maxTime:
                return
            if node == 0:
                res = max(res, pathSum)
            for adjN in adj[node]:
                w = adj[node][adjN]
                if adjN not in pathSet:
                    pathSet.add(adjN)
                    dfs(adjN, pathSet, pathSum + values[adjN], currTime + w)
                    pathSet.remove(adjN)
                else:
                    dfs(adjN, pathSet, pathSum, currTime + w)
        
        dfs(0, {0}, values[0], 0)

        return res
            
            