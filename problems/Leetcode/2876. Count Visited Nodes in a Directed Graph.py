class Solution:
    def countVisitedNodes(self, edges: List[int]) -> List[int]:
        # compute which nodes are in cycles and the size of their cycles

        cycles = []

        seen = set()

        def dfs(node, pathSet, path):
            nxt = edges[node]
            seen.add(node)
            if nxt in pathSet:
                cycle = []
                while path[-1] != nxt:
                    cycle.append(path.pop())
                cycle.append(nxt)
                cycles.append(cycle)
                return
            if nxt in seen:
                return
            pathSet.add(nxt)
            path.append(nxt)
            dfs(nxt, pathSet, path)
        
        n = len(edges)
        for node in range(n):
            if node in seen:
                continue
            dfs(node, {node}, [node])
        
        nodeToCycleLengths = {} # node -> length of the cycle it is in

        for cycle in cycles:
            for node in cycle:
                nodeToCycleLengths[node] = len(cycle)
        
            
        @cache
        def dp(node):
            if edges[node] in nodeToCycleLengths:
                return 1 + nodeToCycleLengths[edges[node]]
            return 1 + dp(edges[node])
        

        res = []
        for node in range(n):
            if node in nodeToCycleLengths:
                res.append(nodeToCycleLengths[node])
            else:
                res.append(dp(node))
        
        return res