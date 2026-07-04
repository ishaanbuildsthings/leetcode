# root = the root node (usually 0 or 1), separate from if the nodes are 0...n-1 or 1...n
# edges = [[a, b], [c, d], ...]
# vals = raw data for the edge ABOVE each node (the edge from that node to its parent)
# vals[root] is a dummy and is never read
# if zeroIndexed=False then vals[0] in addition to vals[root] is a dummy
# base = (rawEdge) -> mapped val
# merge(edgeVal1, edgeVal2) -> edgeVal3
# zeroIndexed=True means nodes are from 0...n-1, otherwise 1...n
class LiftEdge:
    # O(n log n) build time and space
    def __init__(self, root, edges, vals, base, merge, zeroIndexed=True):
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
                self.upData[0][node] = base(vals[node])
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

    # aggregated edgeValue for the k edges going up from `node` (edge above node first), None if k==0
    # O(log N)
    def liftQuery(self, node, k):
        acc = None
        rem = k
        for b in range(self.LOG - 1, -1, -1):
            if rem >= (1 << b):
                d = self.upData[b][node]
                if d is not None:
                    acc = d if acc is None else self.merge(acc, d)
                node = self.up[b][node]
                rem -= (1 << b)
        return acc

    # aggregated edgeValue for the A<>B path (edge above the LCA is NOT on the path); None if A==B
    # O(log N)
    def pathQuery(self, a, b):
        l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        left = self.liftQuery(a, da) if da > 0 else None
        right = self.liftQuery(b, db) if db > 0 else None
        if left is None:
            return right
        if right is None:
            return left
        return self.merge(left, right)

    # lca of a and b if the tree were rooted at r instead of the build root
    # O(log N)
    def lcaUnderR(self, r, a, b):
        return self.median(a, b, r)