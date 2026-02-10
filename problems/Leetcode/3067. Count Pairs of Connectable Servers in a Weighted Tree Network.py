class Solution:
    def countPairsOfConnectableServers(self, edges: List[List[int]], signalSpeed: int) -> List[int]:
        n = len(edges) + 1
        g = [[] for _ in range(n)] # g[node] -> [(adjN, adjW), ...]
        for a, b, w in edges:
            g[a].append((b, w))
            g[b].append((a, w))
    
        def forRoot(root):
            answer = 0
            distMap = [0] * n
            def dfs(node, parent, dist):
                distMap[node] = dist
                for adjN, adjW in g[node]:
                    if adjN == parent:
                        continue
                    dfs(adjN, node, dist + adjW)
            dfs(root, -1, 0)
            divis = 0
            # find how many are divisible in this subtree
            def procedure(node, parent):
                resHere = 0
                if distMap[node] % signalSpeed == 0:
                    resHere += 1
                for adjN, _ in g[node]:
                    if adjN == parent:
                        continue
                    resHere += procedure(adjN, node)
                return resHere


            for adjN, _ in g[root]:
                newCount = procedure(adjN, root)
                answer += divis * newCount
                divis += newCount
            
            return answer


        
        res = [0] * n
        for node in range(n):
            res[node] = forRoot(node)
        
        return res


