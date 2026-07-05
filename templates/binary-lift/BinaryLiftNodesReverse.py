# TEMPLATE BY ISHAANBUILDSTHINGS
# root = the root node (usually 0 or 1), separate from if the nodes are 0...n-1 or 1...n
# edges = [[a, b], [c, d], ...]
# vals = list of raw node values, if zeroIndexed=False, then vals[0] can be any dummy value
# base = (rawVal) -> mapped val
# merge(leftData, rightData) -> data   (NON-commutative; left is closer to A on the path)
# reverse(data) -> data as if its underlying segment were traversed the other way
#   (for max-subsegment: swap prefix<->suffix; for a plain sum/min/max: return data unchanged)
# zeroIndexed=True means nodes are from 0...n-1, otherwise 1...n
class Lift:
    # O(n log n) build time and space
    def __init__(self, root, edges, vals, base, merge, reverse, zeroIndexed):
        self.n = len(edges) + (1 if zeroIndexed else 2)
        self.LOG = max(1, self.n.bit_length())
        self.vals = vals
        self.base = base
        self.merge = merge
        self.reverse = reverse

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
                lo = self.upData[k - 1][node]
                hi = self.upData[k - 1][mid]
                if lo is None:
                    self.upData[k][node] = hi
                elif hi is None:
                    self.upData[k][node] = lo
                else:
                    self.upData[k][node] = merge(hi, lo)
            stack.append((node, parent, True))
            for child in g[node]:
                if child != parent:
                    stack.append((child, node, False))

    # kth steps above `node`; returns root if k shoots past the root.  O(log N)
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

    # data over the k nodes from `node` going up (node included), in top-down
    # path order (shallow -> deep).  None if k == 0.  O(log N)
    def liftQuery(self, node, k):
        acc = None
        rem = k
        for b in range(self.LOG - 1, -1, -1):
            if rem >= (1 << b):
                d = self.upData[b][node]
                if d is not None:
                    acc = d if acc is None else self.merge(d, acc)
                node = self.up[b][node]
                rem -= (1 << b)
        return acc

    # aggregated data over the path A -> B, read in that direction (NON-commutative).  O(log N)
    def pathQuery(self, a, b):
        l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        res = self.base(self.vals[l])
        if da > 0:
            res = self.merge(self.reverse(self.liftQuery(a, da)), res)
        if db > 0:
            res = self.merge(res, self.liftQuery(b, db))
        return res