class Solution:
    def calcEquation(self, equations: List[List[str]], values: List[float], queries: List[List[str]]) -> List[float]:

        nodes = set()
        for a, b in equations:
            nodes.add(a)
            nodes.add(b)
        nodes = list(nodes)
        n = len(nodes)
        nodeToIdx = {
            node : idx for idx, node in enumerate(nodes)
        }
        
        adj = defaultdict(list) # holds (adjN, w)
        for i in range(len(equations)):
            a, b = equations[i]
            id1 = nodeToIdx[a]
            id2 = nodeToIdx[b]
            v = values[i]
            adj[id1].append((id2, v))
            adj[id2].append((id1, 1 / v))
        
        components = [None] * n # maps node id -> component id
        distFromRoot = [None] * n # distFromRoot[nodeId] tells us the distance from that root

        def dfs(nodeId, componentId, dist, rootId):
            components[nodeId] = componentId
            distFromRoot[nodeId] = dist
            for adjN, adjW in adj[nodeId]:
                if components[adjN] is not None:
                    continue
                dfs(adjN, componentId, dist * adjW, rootId)
       

        componentId = 0
        for nodeId in range(n):
            if components[nodeId] is not None:
                continue
            dfs(nodeId, componentId, 1, nodeId)
            componentId += 1
        
        res = []
        for a, b in queries:
            if a not in nodeToIdx or b not in nodeToIdx:
                res.append(-1)
                continue
            a = nodeToIdx[a]
            b = nodeToIdx[b]
            if components[a] != components[b]:
                res.append(-1)
                continue
            compId = components[a]
            d1 = distFromRoot[a]
            d2 = distFromRoot[b]
            res.append(d2 / d1)
        
        return res
            
        