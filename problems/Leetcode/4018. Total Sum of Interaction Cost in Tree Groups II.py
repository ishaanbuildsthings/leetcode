# SOLUTION 1, CENTROID DECOMP

# O(n log n)
# pass in a list of edges [(a, b), (c, d), ...]
# get out a list of [(subtreeRoot, { node1 : node1Children, node2 : node2Children, ...}), ...]
# with edges == [] it returns [(0, {0: []})]
def centroidDecomp(edges):
    arrSize = 1
    for u, v in edges:
        if u >= arrSize: arrSize = u + 1
        if v >= arrSize: arrSize = v + 1
    adj = [[] for _ in range(arrSize)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    removed = [False] * arrSize
    sz = [0] * arrSize
    par = [-1] * arrSize
    res = []
    stack = [edges[0][0] if edges else 0]
    while stack:
        start = stack.pop()
        order = []
        dfs = [start]
        par[start] = -1
        while dfs:
            node = dfs.pop()
            order.append(node)
            for nxt in adj[node]:
                if nxt != par[node] and not removed[nxt]:
                    par[nxt] = node
                    dfs.append(nxt)
        total = len(order)
        for node in order:
            sz[node] = 1
        for node in reversed(order):
            if par[node] != -1:
                sz[par[node]] += sz[node]
        centroid = start
        while True:
            heavy = -1
            for nxt in adj[centroid]:
                if nxt != par[centroid] and not removed[nxt] and sz[nxt] * 2 > total:
                    heavy = nxt
                    break
            if heavy == -1:
                break
            centroid = heavy
        children = {centroid: []}
        bfs = [centroid]
        while bfs:
            node = bfs.pop()
            kids = children[node]
            for nxt in adj[node]:
                if not removed[nxt] and nxt not in children:
                    children[nxt] = []
                    kids.append(nxt)
                    bfs.append(nxt)
        res.append((centroid, children))
        removed[centroid] = True
        for nxt in adj[centroid]:
            if not removed[nxt]:
                stack.append(nxt)
    return res

class Solution:
    def interactionCosts(self, n: int, edges: list[list[int]], group: list[int]) -> int:
        trees = centroidDecomp(edges)
        
        def solveForTree(treeTup):
            root, children = treeTup
            res = 0

            def collect(node, gToSum, gFrq, currDepth):
                g = group[node]
                gToSum[g] += currDepth
                gFrq[g] += 1
                for child in children[node]:
                    collect(child, gToSum, gFrq, currDepth + 1)
            
            rootChildren = []
            for child in children[root]:
                gToSum = defaultdict(int)
                gFrq = defaultdict(int)
                collect(child, gToSum, gFrq, 1)
                rootChildren.append((gToSum, gFrq))

            accSum = defaultdict(int) # accumulated sum of group -> root distances for all paths
            accCount = defaultdict(int) # accumulated count of group -> root count of paths
            accCount[group[root]] += 1

            for childSum, childFrq in rootChildren:
                # new path total distances, for each group, its sum is going to occur the previous amount of count times
                # and the previous sum is going to add the new count
                for g in childSum:
                    total = childSum[g]
                    frq = childFrq[g]

                    newPathSum = 0
                    newPathSum += total * accCount[g]
                    newPathSum += accSum[g] * frq
                    res += newPathSum

                    accSum[g] += childSum[g]
                    accCount[g] += childFrq[g]
            
            return res

        return sum(solveForTree(tree) for tree in trees)


        




# SOLUTION 2, SMALL TO LARGE MERGING WITH SHIFTING
# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings

# edgeList = [[a, b], [c, d], ...]
# if zeroIndex is true, assumes the root is 0, returns an array `children` that goes up to `children[n-1]` (n-1 is inferred from the edgeList)
# if zeroIndex is false, assumes the root is 1, returns an array `children` that goes up to `children[n]`, children[0] is empty and unused
# def edgeListToTree(edgeList, zeroIndexed=True):
#     n = len(edgeList) + 1
#     size = n if zeroIndexed else n + 1
#     root = 0 if zeroIndexed else 1
#     edgeMap = [[] for _ in range(size)]
#     for a, b in edgeList:
#         edgeMap[a].append(b)
#         edgeMap[b].append(a)
#     children = [[] for _ in range(size)]
#     parent = [-1] * size
#     stack = [root]
#     while stack:
#         node = stack.pop()
#         for adj in edgeMap[node]:
#             if adj == parent[node]:
#                 continue
#             parent[adj] = node
#             children[node].append(adj)
#             stack.append(adj)
#     return children

# class Bucket:
#     def __init__(self):
#         self.dist = defaultdict(int) # maps group key to sum of distances to root
#         self.frq = defaultdict(int) # maps group key to fequency
#         self.shift = 0
    
#     def shiftPlus(self):
#         self.shift += 1
    
#     def add(self, g, frqGain, sumGain):
#         self.frq[g] += frqGain
#         self.dist[g] += sumGain - frqGain * self.shift
    
#     def data(self):
#         res = []
#         for k, v in self.frq.items():
#             res.append((k, v, self.dist[k] + (self.shift * self.frq[k])))
#         return res
    
#     def getFrq(self, g):
#         return self.frq[g]
    
#     def getSumDist(self, g):
#         ans = self.dist[g]
#         return ans + (self.frq[g] * self.shift)
    

# class Solution:
#     def interactionCosts(self, n: int, edges: list[list[int]], group: list[int]) -> int:
#         children = edgeListToTree(edges)
#         res = 0

#         def dfs(node):
#             nonlocal res
#             g = group[node]
#             if not children[node]:
#                 b = Bucket()
#                 b.add(g, 1, 0)
#                 b.shiftPlus()
#                 return b
            
#             childs = []
#             for child in children[node]:
#                 childs.append(dfs(child))
            
#             childs.sort(key=lambda x : len(x.frq), reverse=True)
#             acc = childs[0]

#             # all of the initial ones can connect to the root
#             res += acc.getSumDist(g)
#             acc.add(g, 1, 0) # add root as an endpoint point


#             for childBucket in childs[1:]:
#                 for grp, frq, sumDist in childBucket.data():
#                     totalPathGain = frq * acc.getSumDist(grp)
#                     totalPathGain += acc.getFrq(grp) * sumDist
#                     res += totalPathGain
#                 for grp, frq, sumDist in childBucket.data():
#                     acc.add(grp, frq, sumDist)
            
#             acc.shiftPlus()
#             return acc

#         dfs(0)

#         return res