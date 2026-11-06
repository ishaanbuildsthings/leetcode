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
    def longestSpecialPath(self, edges: List[List[int]], nums: List[int]) -> List[int]:
        
        edges2 = [(a, b) for a, b, w in edges]
        edgeToW = {}
        for a, b, w in edges:
            edgeToW[a, b] = edgeToW[b, a] = w

        children = edgeListToTree(edges2, 0)

        n = len(edges) + 1
        LOG = n.bit_length() + 1
        parents = [-1] * n
        for node in range(n):
            for child in children[node]:
                parents[child] = node
            
        depthOccs = defaultdict(list) # maps a value to depths it is occurring at
        nodeToNextAbove = [-1] * n
        nodeToDepths = [None] * n

        def dfs(node, depth):
            nodeToDepths[node] = depth
            v = nums[node]
            if depthOccs[v]:
                nodeToNextAbove[node] = depthOccs[v][-1]
            depthOccs[v].append(depth)
            for child in children[node]:
                dfs(child, depth + 1)
            depthOccs[v].pop()
        
        dfs(0, 0)

        fmax = lambda x, y : x if x > y else y

        def mergeNodeData(d1, d2):
            return top2(*d1, *d2)
        
        def mergeData(d1, d2):
            nodes = mergeNodeData(d1[0], d2[0])
            tot = d1[1] + d2[1]
            return nodes, tot, d2[2]
        
        def top2(a, b, c, d):
            if a >= c:
                return a, fmax(b, c)
            return c, fmax(d, a)
        
        cache = [[None for _ in range(LOG)] for _ in range(n)]
        
        def pathAgg(node, power):
            if power == 0:
                parent = parents[node] if parents[node] != -1 else node
                nodeData = nodeToNextAbove[node], -inf
                edgeData = edgeToW[node, parents[node]] if node != 0 else 0
                return parent, nodeData, edgeData
            if cache[node][power]:
                return cache[node][power]
            halfNode, firstNodes, firstSum = pathAgg(node, power - 1)
            endNode, secondNodes, secondSum = pathAgg(halfNode, power - 1)
            cache[node][power] = endNode, mergeNodeData(firstNodes, secondNodes), firstSum + secondSum
            return cache[node][power]
        
        res = [-inf, inf]
        for node in range(n):
            depth = nodeToDepths[node]
            curr = node
            pathSum = 0
            numNodes = 1
            deepest1, deepest2 = -inf, -inf
            powed = 2**(LOG - 1)
            for b in range(LOG - 1, -1, -1):
                jumped, (deep1, deep2), dist = pathAgg(curr, b)
                new1, new2 = top2(deepest1, deepest2, deep1, deep2)
                chainHeadDepth = fmax(0, nodeToDepths[curr] - (powed))
                powed //= 2
                if new2 < chainHeadDepth:
                    curr = jumped
                    pathSum += dist
                    numNodes = depth - chainHeadDepth + 1
                    deepest1, deepest2 = new1, new2
            if pathSum > res[0]:
                res[0] = pathSum
                res[1] = numNodes
            elif pathSum == res[0]:
                res[1] = min(res[1], numNodes)
                
        return res
            
                