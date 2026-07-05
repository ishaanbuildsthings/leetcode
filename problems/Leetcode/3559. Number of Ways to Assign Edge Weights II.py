n = 3
LOG = 1
depths = { 0 : 0, 1 : 1, 2 : 2 }
parents = { 0 : 0, 1 : 0, 2 : 1 }

# ______________________________________________________________________
# TEMPLATE - binary lifting

# FUNCTIONS:
# Query LCA: O(logN)
# Query kth ancestor of a node: O(logN)
# Query distance between two nodes: O(logN)
# Get a list of all nodes on the path between two nodes: O(path)

# General reqs:
# An arbitrarily rooted tree or a directed graph works.

# Time Complexity:
# Preprocess: O(NlogN)

# VARIABLE REQUIREMENTS:
# n is the number of nodes
# depths[node] tells us the depth
# parents[node] tells us the parent, if we are at a root in a tree or parent, IT MUST POINT TO ITSELF
# LOG floor(log2(n)). This is the biggest jump we need to make. If n is a power of 2, technically we can jump less. However, if n=1, LOG is 0. If we say we need to make no jumps, the may get messed up. It's also harder to code that LOG can be 1 less if n is a power of 2.

# construct the lift table which will help us compute the LCA
# lift[node][jumpPow] tells us the 2^power-th ancestor of node, always ending at 0


class Solution:
    def assignEdgeWeights(self, edges: List[List[int]], queries: List[List[int]]) -> List[int]:
        def buildLifting(adj, n):
            parents = [0] * n
            depths = [0] * n

            def dfs(node, parent):
                for nxt in adj[node]:
                    if nxt == parent:
                        continue
                    parents[nxt] = node
                    depths[nxt] = depths[node] + 1
                    dfs(nxt, node)

            dfs(0, -1)

            LOG = (n - 1).bit_length()
            
            lift = [[0] * (LOG + 1) for _ in range(n)]
            for i in range(n):
                lift[i][0] = parents[i]
            for j in range(1, LOG + 1):
                for i in range(n):
                    lift[i][j] = lift[lift[i][j - 1]][j - 1]

            def getKthAncestor(node, k):
                bit = 0
                while k:
                    if k & 1:
                        node = lift[node][bit]
                    k >>= 1
                    bit += 1
                return node

            def getLca(u, v):
                if depths[u] < depths[v]:
                    u, v = v, u
                u = getKthAncestor(u, depths[u] - depths[v])
                if u == v:
                    return u
                for j in range(LOG, -1, -1):
                    if lift[u][j] != lift[v][j]:
                        u = lift[u][j]
                        v = lift[v][j]
                return parents[u]

            def getDistance(u, v):
                w = getLca(u, v)
                return depths[u] + depths[v] - 2 * depths[w]

            return getDistance
        
        adj = defaultdict(list)
        for a, b in edges:
            adj[a-1].append(b-1)
            adj[b-1].append(a-1)
        
        getDist = buildLifting(adj, len(edges) + 1)

        
        # for each query, find LCA
        # find # of edges to parent
        # find number of ways to make a path odd and even with DP
        MOD = 10**9 + 7
        @cache
        def waysToMakeOdd(edges, isOddCurrently):
            if edges == 0:
                return 1 if isOddCurrently else 0
            ifPlaceOddHere = waysToMakeOdd(edges - 1, not isOddCurrently)
            ifPlaceEven = waysToMakeOdd(edges - 1, isOddCurrently)
            return (ifPlaceOddHere + ifPlaceEven) % MOD
        
        # @cache
        # def waysToMakeEven(edges, isEvenCurrently):
        #     if edges == 0:
        #         return 1 if isEvenCurrently else 0
        #     ifPlaceOddHere = waysToMakeEven(edges - 1, not isEvenCurrently)
        #     ifPlaceEven = waysToMakeEven(edges - 1, isEvenCurrently)
        #     return (ifPlaceOddHere + ifPlaceEven) % MOD
        
        
        res = []
        
        for a, b in queries:
            a -= 1
            b -= 1
            pathLength = getDist(a, b)
            res.append(waysToMakeOdd(pathLength, False))
        waysToMakeOdd.cache_clear()
        return res
#             LCA = getLca(a, b)
#             print(LCA)
            