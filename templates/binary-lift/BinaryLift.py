class Lift:
    def __init__(self, root, edges, vals, base, merge):
        self.n = len(edges) + 1
        self.LOG = max(1, self.n.bit_length())
        self.vals = vals
        self.base = base
        self.merge = merge

        g = [[] for _ in range(self.n)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        self.depths = [0] * self.n
        self.up = [[0] * self.n for _ in range(self.LOG)]
        self.upData = [[None] * self.n for _ in range(self.LOG)]

        stack = [(root, root, False)]
        while stack:
            node, parent, visited = stack.pop()
            if visited:
                continue
            self.depths[node] = 0 if node == root else self.depths[parent] + 1
            self.up[0][node] = parent
            if node != root:
                self.upData[0][node] = base(vals[parent])
            for k in range(1, self.LOG):
                mid = self.up[k - 1][node]
                self.up[k][node] = self.up[k - 1][mid]
                a = self.upData[k - 1][node]
                b = self.upData[k - 1][mid]
                if a is None:
                    self.upData[k][node] = b
                elif b is None:
                    self.upData[k][node] = a
                else:
                    self.upData[k][node] = merge(a, b)
            stack.append((node, parent, True))
            for child in g[node]:
                if child != parent:
                    stack.append((child, node, False))

    def kthAncestor(self, a, kth):
        for k in range(self.LOG):
            if (kth >> k) & 1:
                a = self.up[k][a]
        return a

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

    def pathDist(self, a, b):
        ab = self.lca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[ab]

    def geodesic(self, a, b, c):
        return self.lca(a, b) ^ self.lca(a, c) ^ self.lca(b, c)

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

    def distToPath(self, a, b, x):
        return self.pathDist(self.geodesic(a, b, x), x)

    def inPath(self, a, b, x):
        return self.geodesic(a, b, x) == x

    def liftQuery(self, v, cnt):
        acc = self.base(self.vals[v])
        rem = cnt - 1
        for k in range(self.LOG - 1, -1, -1):
            if rem >= (1 << k):
                d = self.upData[k][v]
                if d is not None:
                    acc = self.merge(acc, d)
                v = self.up[k][v]
                rem -= (1 << k)
        return acc

    def pathQuery(self, a, b, l=None):
        if l is None:
            l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        res = self.base(self.vals[l])
        if da > 0:
            res = self.merge(self.liftQuery(a, da), res)
        if db > 0:
            res = self.merge(res, self.liftQuery(b, db))
        return res