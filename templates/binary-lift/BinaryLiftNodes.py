# TEMPLATE BY ISHAANBUILDSTHINGS
# root = the root node (usually 0 or 1), separate from if the nodes are 0...n-1 or 1...n
# edges = [[a, b], [c, d], ...]
# vals = list of raw node values, if zeroIndexed=False, then vals[0] can be any dummy value
# base = (rawVal) -> mapped val
# merge(nodeVal1, nodeVal2) -> nodeVal3
# zeroIndexed=True means nodes are from 0...n-1, otherwise 1...n
class Lift:
    # O(n log n) build time and space
    def __init__(self, root, edges, vals, base, merge, zeroIndexed):
        self.n = len(edges) + (1 if zeroIndexed else 2)
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

    # kth steps above `node`
    # always returns root if k steps shoots past the root
    # O(log N)
    def kthAncestor(self, node, kth):
        for k in range(self.LOG):
            if (kth >> k) & 1:
                node = self.up[k][node]
        return node

    # O(log N)
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

    # unweighted path distance from A<>B
    # O(log N)
    def pathDist(self, a, b):
        ab = self.lca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[ab]

    # the median node, which is the only node on all three paths: A<>B, B<>C, A<>C
    # O(log N)
    def median(self, a, b, c):
        return self.lca(a, b) ^ self.lca(a, c) ^ self.lca(b, c)

    # k-th node on the A->B path, 1-indexed
    # -1 if OOB
    # O(log N)
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

    # how many edges to cross to get from `node` onto any node on the A<>B path
    # O(log N)
    def distToPath(self, a, b, node):
        return self.pathDist(self.median(a, b, node), node)

    # returns a bool if `node` is on the path A<>B
    # O(log N)
    def inPath(self, a, b, node):
        return self.median(a, b, node) == node

    # gives us the aggregated nodeValue for the upwards path k nodes long, so k=1 means just node
    # O(log N)
    def liftQuery(self, node, k):
        acc = self.base(self.vals[node])
        rem = k - 1
        for b in range(self.LOG - 1, -1, -1):
            if rem >= (1 << b):
                d = self.upData[b][node]
                if d is not None:
                    acc = self.merge(acc, d)
                node = self.up[b][node]
                rem -= (1 << b)
        return acc

    # gives us the aggregated nodeValue for the A<>B path
    # O(log N)
    def pathQuery(self, a, b):
        l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        res = self.base(self.vals[l])
        if da > 0:
            res = self.merge(self.liftQuery(a, da), res)
        if db > 0:
            res = self.merge(res, self.liftQuery(b, db))
        return res

    # lca of a and b if the tree were rooted at r instead of the build root
    # O(log N)
    def lcaUnderR(self, r, a, b):
        return self.median(a, b, r)


    # intersection of path a<>b and path x<>y.
    # returns (p, q) endpoints of the shared subpath (p==q if single node), or None if disjoint.
    # O(log N)
    def pathIntersection(self, a, b, x, y):
        # candidate endpoints: project each path's "corners" onto the other path
        cands = [
            self.median(a, b, x), self.median(a, b, y),
            self.median(x, y, a), self.median(x, y, b),
        ]
        # keep only nodes lying on BOTH paths
        onBoth = [c for c in cands if self.inPath(a, b, c) and self.inPath(x, y, c)]
        if not onBoth:
            return None
        # the intersection is a subpath; its endpoints are the two farthest-apart survivors
        p = q = onBoth[0]
        best = -1
        for i in range(len(onBoth)):
            for j in range(i, len(onBoth)):
                d = self.pathDist(onBoth[i], onBoth[j])
                if d > best:
                    best = d
                    p, q = onBoth[i], onBoth[j]
        return (p, q)