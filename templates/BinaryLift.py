class Lift:
    def __init__(self, root, numNodes, g):
        # g[node] = list of adjacent nodes
        self.root = root
        self.numNodes = numNodes
        self.LOG = max(1, numNodes.bit_length())
        self.depths = [0] * numNodes
        self.up = [[0] * numNodes for _ in range(self.LOG)]

        # O(n log n) - build depths and ancestor table via iterative DFS
        stack = [(root, root, False)]
        while stack:
            node, parent, visited = stack.pop()
            if visited:
                continue
            self.depths[node] = 0 if node == root else self.depths[parent] + 1
            self.up[0][node] = parent
            for k in range(1, self.LOG):
                self.up[k][node] = self.up[k - 1][self.up[k - 1][node]]
            stack.append((node, parent, True))
            for child in g[node]:
                if child != parent:
                    stack.append((child, node, False))

    # O(log n) - get kth ancestor of a, or root if overshooting
    def kthAncestor(self, a, kth):
        for k in range(self.LOG):
            if (kth >> k) & 1:
                a = self.up[k][a]
        return a

    # O(log n) - lowest common ancestor of a and b
    def lca(self, a, b):
        if self.depths[a] < self.depths[b]:
            a, b = b, a
        diff = self.depths[a] - self.depths[b]
        for k in range(self.LOG):
            if (diff >> k) & 1:
                a = self.up[k][a]
        if a == b:
            return a
        for k in range(self.LOG - 1, -1, -1):
            if self.up[k][a] != self.up[k][b]:
                a = self.up[k][a]
                b = self.up[k][b]
        return self.up[0][a]

    # O(log n) - edge distance between a and b
    def pathDist(self, a, b):
        ab = self.lca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[ab]

    # O(log n) - unique node on all three pairwise paths between a, b, c
    def geodesic(self, a, b, c):
        return self.lca(a, b) ^ self.lca(a, c) ^ self.lca(b, c)

    # O(log n) - kth node on path a->b (1-indexed, a is 1st). returns -1 if out of range
    def kthOnPath(self, a, b, kth):
        ab = self.lca(a, b)
        distA = self.depths[a] - self.depths[ab]
        distB = self.depths[b] - self.depths[ab]
        totalLen = distA + distB + 1
        if kth < 1 or kth > totalLen:
            return -1
        if kth <= distA + 1:
            return self.kthAncestor(a, kth - 1)
        return self.kthAncestor(b, distB - (kth - distA - 1))

    # O(log n) - shortest distance from x to the path a<->b
    def distToPath(self, a, b, x):
        return self.pathDist(self.geodesic(a, b, x), x)

    # O(log n) - checks if x lies on the path a<->b
    def inPath(self, a, b, x):
        return self.geodesic(a, b, x) == x