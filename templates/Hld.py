class Hld:
    def __init__(self, n, edges, vals, baseFn, mergeFn, identity):
        self.n = n
        self.vals = list(vals)
        self.baseFn = baseFn
        self.mergeFn = mergeFn
        self.identity = identity
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        self.parent = [0] * n
        self.depth = [0] * n
        self.sz = [1] * n
        self.heavy = [-1] * n
        self.head = [0] * n
        self.pos = [0] * n
        self.curPos = 0
        self._dfs(adj, 0)
        self._decompose(adj, 0)
        self._buildSegTree()

    def _dfs(self, adj, root):
        stack = [(root, -1, False)]
        while stack:
            u, p, visited = stack.pop()
            if visited:
                for v in adj[u]:
                    if v != p:
                        self.sz[u] += self.sz[v]
                        if self.heavy[u] == -1 or self.sz[v] > self.sz[self.heavy[u]]:
                            self.heavy[u] = v
                continue
            self.parent[u] = p
            stack.append((u, p, True))
            for v in adj[u]:
                if v != p:
                    self.depth[v] = self.depth[u] + 1
                    self.parent[v] = u
                    stack.append((v, u, False))

    def _decompose(self, adj, root):
        stack = [(root, root)]
        while stack:
            u, h = stack.pop()
            self.head[u] = h
            self.pos[u] = self.curPos
            self.curPos += 1
            light = []
            for v in adj[u]:
                if v != self.parent[u] and v != self.heavy[u]:
                    light.append(v)
            for v in light:
                stack.append((v, v))
            if self.heavy[u] != -1:
                stack.append((self.heavy[u], h))

    def _buildSegTree(self):
        self.tree = [None] * (4 * self.n)
        ordered = [None] * self.n
        for i in range(self.n):
            ordered[self.pos[i]] = self.vals[i]
        self._build(1, 0, self.n - 1, ordered)

    def _build(self, node, l, r, ordered):
        if l == r:
            self.tree[node] = self.baseFn(ordered[l])
            return
        mid = (l + r) // 2
        self._build(2 * node, l, mid, ordered)
        self._build(2 * node + 1, mid + 1, r, ordered)
        self.tree[node] = self.mergeFn(self.tree[2 * node], self.tree[2 * node + 1])

    def _update(self, node, l, r, idx, val):
        if l == r:
            self.tree[node] = self.baseFn(val)
            return
        mid = (l + r) // 2
        if idx <= mid:
            self._update(2 * node, l, mid, idx, val)
        else:
            self._update(2 * node + 1, mid + 1, r, idx, val)
        self.tree[node] = self.mergeFn(self.tree[2 * node], self.tree[2 * node + 1])

    def _query(self, node, l, r, ql, qr):
        if ql > r or qr < l:
            return self.identity
        if ql <= l and r <= qr:
            return self.tree[node]
        mid = (l + r) // 2
        left = self._query(2 * node, l, mid, ql, qr)
        right = self._query(2 * node + 1, mid + 1, r, ql, qr)
        return self.mergeFn(left, right)

    def update(self, u, val):
        self.vals[u] = val
        self._update(1, 0, self.n - 1, self.pos[u], val)

    def query(self, u, v):
        res = self.identity
        while self.head[u] != self.head[v]:
            if self.depth[self.head[u]] < self.depth[self.head[v]]:
                u, v = v, u
            res = self.mergeFn(res, self._query(1, 0, self.n - 1, self.pos[self.head[u]], self.pos[u]))
            u = self.parent[self.head[u]]
        if self.depth[u] > self.depth[v]:
            u, v = v, u
        res = self.mergeFn(res, self._query(1, 0, self.n - 1, self.pos[u], self.pos[v]))
        return res

# what gets stored in a node
def basefn(v):
    pass
def mergefn(node1Data, node2Data):
    pass
identity = # put the identity value here for the mergefn