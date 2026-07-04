class Solution:
    def findMedian(self, n: int, edges: List[List[int]], queries: List[List[int]]) -> List[int]:
        adjMap = defaultdict(list)
        for u, v, w in edges:
            adjMap[u].append((v, w))
            adjMap[v].append((u, w))

        parents = [None] * n
        depths = [0] * n
        distRoot = [0] * n
        children = defaultdict(list)

        def dfs(node, parent):
            for nxt, w in adjMap[node]:
                if nxt == parent:
                    continue
                parents[nxt] = node
                depths[nxt] = depths[node] + 1
                distRoot[nxt] = distRoot[node] + w
                children[node].append(nxt)
                dfs(nxt, node)
        parents[0] = -1
        dfs(0, -1)

        maxPow = n.bit_length()

        @cache
        def ancestor(node, power):
            if node == -1:
                return -1
            if power == 0:
                return parents[node]
            half = ancestor(node, power - 1)
            return ancestor(half, power - 1)

        @cache
        def kthAncestor(node, k):
            if k == 0 or node == -1:
                return node
            bit = k.bit_length() - 1
            return kthAncestor(ancestor(node, bit), k - (1 << bit))

        def lca(a, b):
            if depths[a] < depths[b]:
                a, b = b, a
            diff = depths[a] - depths[b]
            a = kthAncestor(a, diff)
            if a == b:
                return a
            for p in range(maxPow, -1, -1):
                jumpA = ancestor(a, p)
                jumpB = ancestor(b, p)
                if jumpA != jumpB:
                    a = jumpA
                    b = jumpB
            return parents[a]

        def pathWeight(a, b):
            z = lca(a, b)
            return distRoot[a] + distRoot[b] - 2 * distRoot[z]

        def aToBX(a, b, x):
            z = lca(a, b)
            up = depths[a] - depths[z]
            if x <= up:
                return kthAncestor(a, x)
            down = depths[b] - depths[z]
            return kthAncestor(b, down - (x - up))

        res = []
        for a, b in queries:
            tot = pathWeight(a, b)
            z = lca(a, b)
            pathLength = depths[a] + depths[b] - (2 * depths[z]) + 1
            l, r = 0, pathLength - 1
            resNode = b
            while l <= r:
                m = (l+r)//2
                nodeMid = aToBX(a, b, m)
                if pathWeight(a, nodeMid) * 2 >= tot:
                    resNode = nodeMid
                    r = m - 1
                else:
                    l = m + 1
            res.append(resNode)
        return res