# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# edgeList = [[a, b], [c, d], ...]
# roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
# 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
def edgeListToTree(edgeList, root):
    size = max(max(a, b) for a, b in edgeList) + 1
    edgeMap = [[] for _ in range(size)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)
    children = [[] for _ in range(size)]
    parent = [-1] * size
    stack = [root]
    while stack:
        node = stack.pop()
        for adj in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            children[node].append(adj)
            stack.append(adj)
    return children
    
class Solution:
    def minActivationCost(self, edges: list[list[int]], values: list[int]) -> int:
        bitVals = [v.bit_count() % 2 for v in values]
        edges2 = [(a, b) for a, b, w in edges]
        children = edgeListToTree(edges2, 0)
        edgeToW = {}
        for a, b, w in edges:
            edgeToW[a, b] = edgeToW[b, a] = w

        res = inf

        # returns min length path with a total xor equal to 0, and equal to 1
        @cache
        def dfs(node):
            nonlocal res
            if not children[node]:
                if bitVals[node] == 0:
                    return [0, inf]
                return [inf, 0]

            rtVal = bitVals[node]

            minToRoot = [inf, inf]
            for child in children[node]:
                minPathToChild0, minPathToChild1 = dfs(child)
                wt = edgeToW[node, child]

                minToRoot[rtVal] = min(minToRoot[rtVal], wt + minPathToChild0)
                minToRoot[1 ^ rtVal] = min(minToRoot[1 ^ rtVal], wt + minPathToChild1)

            res = min(res, minToRoot[0])

            accNoRoot = [inf, inf]
            for child in children[node]:
                childRes = dfs(child)
                wt = edgeToW[node, child]

                for childXor in range(2):

                    for prevXor in range(2):
    
                        nxor = childXor ^ prevXor ^ rtVal
                        pathDist = wt + accNoRoot[prevXor] + childRes[childXor]
                        if nxor == 0:
                            res = min(res, pathDist)

                for childXor in range(2):
                    npath = wt + childRes[childXor]
                    accNoRoot[childXor] = min(accNoRoot[childXor], npath)

            minToRoot[rtVal] = min(minToRoot[rtVal], 0)

            return minToRoot

        dfs(0)

        return res if res != inf else -1
                
                
                
            
        