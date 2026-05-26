class Solution:
    def checkContradictions(self, equations: List[List[str]], values: List[float]) -> bool:
        nodes = set()
        for a, b in equations:
            nodes.add(a)
            nodes.add(b)
        n = len(nodes)
        nodes = list(nodes)

        nodeToIdx = {
            node : idx for idx, node in enumerate(nodes)
        }

        # don't allow duplicate edges with different sizes
        edgeToSize = {}
        for i in range(len(equations)):
            # bad self loops
            if equations[i][0] == equations[i][1] and values[i] != 1:
                return True

            tup = (equations[i][0], equations[i][1])
            if tup not in edgeToSize:
                edgeToSize[tup] = values[i]
            else:
                v = values[i]
                if v != edgeToSize[tup]:
                    return True

        adj = defaultdict(list) # holds (adjN, w)
        for i in range(len(equations)):
            a, b = equations[i]
            v = values[i]
            adj[nodeToIdx[a]].append((nodeToIdx[b], log(v)))
            adj[nodeToIdx[b]].append((nodeToIdx[a], -1 * log(v)))
        
        distance = [None] * n

        # returns if we fail
        def dfs(node, dist):
            distance[node] = dist
            for adjN, adjW in adj[node]:
                nw = dist + adjW
                if distance[adjN] is not None:
                    if abs(distance[adjN] - nw) > (1 / 10**4):
                        return True # we fail
                    continue
                if dfs(adjN, nw):
                    return True
            return False
        
        for node in range(n):
            if distance[node] is not None:
                continue
            failure = dfs(node, 0)
            if failure:
                return True
        
        return False
            
