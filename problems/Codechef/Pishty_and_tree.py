# 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data, EDGE-WEIGHTED VARIANT
# N = number of nodes, root is node 0
# edges = [(a, b, edgeVal), ...] where edgeVal is the edge's value
# base(val) -> stored data
# combine(data1, data2) -> aggregated data

# Each edge's value is pushed onto its DEEPER endpoint (the child).
# The root has no edge above it, so its slot is unused (None).

# pointSet(node, newEdgeVal) - sets the value of the edge ABOVE `node` (no-op if node is root)
# pointApply(node, delta) - applies delta to the edge above node (e.g. XOR with delta, add delta)
# edgeSet(a, b, newEdgeVal) - sets the value of the edge between adjacent nodes a and b
#   a and b MUST be adjacent in the tree (one is the parent of the other)
# edgeApply(a, b, delta) - applies delta to the edge between adjacent nodes a and b
# pathQuery(a, b) -> aggregated data over EDGES on path a..b
#   pathQuery(a, a) returns None (empty path)
#   pathQuery(a, parent(a)) returns data for that single edge
# subtreeQuery(node) -> aggregated data over edges from node to all descendants
#   (the edge above `node` itself is NOT included)

# hld = HLDEdge(numNodes, edgeListWithVals, baseFn, combineFn)
class HLDEdge:
    def __init__(self, n, edges, base, combine):
        self.n = n
        self.base = base
        self.combine = combine
        self.adj = [[] for _ in range(n)]
        for a, b, edgeVal in edges:
            self.adj[a].append((b, edgeVal))
            self.adj[b].append((a, edgeVal))
        self.par = [-1] * n
        self.depth = [0] * n
        self.sz = [1] * n
        self.heavy = [-1] * n
        self.head = [0] * n
        self.pos = [0] * n
        self.edgeAbove = [None] * n  # value of edge above each node; None for root
        self._dfsInit()
        self._dfsDecompose()
        self.segN = 1
        while self.segN < n:
            self.segN <<= 1
        self.seg = [None] * (2 * self.segN)
        for i in range(n):
            if self.edgeAbove[i] is not None:
                self.seg[self.segN + self.pos[i]] = base(self.edgeAbove[i])
        for i in range(self.segN - 1, 0, -1):
            self.seg[i] = self._combineOpt(self.seg[2*i], self.seg[2*i+1])
    
    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)
    
    def _dfsInit(self):
        order = []
        stack = [(0, -1, 0)]
        while stack:
            node, parent, d = stack.pop()
            self.par[node] = parent
            self.depth[node] = d
            order.append(node)
            for nxt, edgeVal in self.adj[node]:
                if nxt != parent:
                    self.edgeAbove[nxt] = edgeVal
                    stack.append((nxt, node, d + 1))
        for node in reversed(order):
            best = 0
            for nxt, edgeVal in self.adj[node]:
                if nxt == self.par[node]: continue
                self.sz[node] += self.sz[nxt]
                if self.sz[nxt] > best:
                    best = self.sz[nxt]
                    self.heavy[node] = nxt
    
    def _dfsDecompose(self):
        timer = 0
        stack = [(0, 0)]
        while stack:
            node, h = stack.pop()
            self.head[node] = h
            self.pos[node] = timer
            timer += 1
            for nxt, edgeVal in self.adj[node]:
                if nxt == self.par[node] or nxt == self.heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if self.heavy[node] != -1:
                stack.append((self.heavy[node], h))
    
    def pointSet(self, node, newEdgeVal):
        if node == 0: return  # root has no edge above
        p = self.pos[node] + self.segN
        self.seg[p] = self.base(newEdgeVal)
        p >>= 1
        while p:
            self.seg[p] = self._combineOpt(self.seg[2*p], self.seg[2*p+1])
            p >>= 1
    
    def pointApply(self, node, delta):
        if node == 0: return
        p = self.pos[node] + self.segN
        self.seg[p] = self._combineOpt(self.seg[p], self.base(delta))
        p >>= 1
        while p:
            self.seg[p] = self._combineOpt(self.seg[2*p], self.seg[2*p+1])
            p >>= 1
    
    # a and b must be adjacent in the tree; the deeper one is the child whose slot stores this edge
    def edgeSet(self, a, b, newEdgeVal):
        child = a if self.depth[a] > self.depth[b] else b
        self.pointSet(child, newEdgeVal)
    
    def edgeApply(self, a, b, delta):
        child = a if self.depth[a] > self.depth[b] else b
        self.pointApply(child, delta)
    
    def _rangeQuery(self, ql, qr):
        if ql > qr: return None
        res = None
        ql += self.segN
        qr += self.segN + 1
        while ql < qr:
            if ql & 1:
                res = self._combineOpt(res, self.seg[ql])
                ql += 1
            if qr & 1:
                qr -= 1
                res = self._combineOpt(res, self.seg[qr])
            ql >>= 1
            qr >>= 1
        return res
    
    # Path query over EDGES from a to b. Skips the LCA's slot since that represents
    # the edge ABOVE the LCA, which is not on the a-b path.
    def pathQuery(self, a, b):
        res = None
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] < self.depth[self.head[b]]:
                a, b = b, a
            chain = self._rangeQuery(self.pos[self.head[a]], self.pos[a])
            res = self._combineOpt(res, chain)
            a = self.par[self.head[a]]
        if self.depth[a] > self.depth[b]:
            a, b = b, a
        # a is the LCA; skip its slot by querying [pos[a]+1, pos[b]]
        last = self._rangeQuery(self.pos[a] + 1, self.pos[b])
        return self._combineOpt(res, last)
    
    # subtree edge query: edges from node down to all its descendants
    # = all stored slots in subtree EXCEPT node's own (which is the edge above node, not in subtree)
    def subtreeQuery(self, node):
        return self._rangeQuery(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1)
def base(edgeVal):
    return edgeVal

def agg(a, b):
    return a ^ b

def solve():
    n = int(input())
    edges = []
    for _ in range(n - 1):
        a, b, c = list(map(int, input().split()))
        a -= 1
        b -= 1
        edges.append((a, b, c))
    m = int(input())
    queries = [] # holds (node1, node2, k, queryIndex)
    for i in range(m):
        a, b, k = list(map(int, input().split()))
        a -= 1
        b -= 1
        queries.append((a, b, k, i))
    queries.sort(key=lambda x: x[2])

    initEdges = []
    for a, b, c in edges:
        initEdges.append((a, b, 0))
    
    hld = HLDEdge(n, initEdges, base, agg)

    edges.sort(key=lambda x: x[2])
    edgeI = 0

    queryAnswers = [None] * m
    for a, b, k, queryI in queries:
        while edgeI < len(edges) and edges[edgeI][2] <= k:
            hld.edgeApply(edges[edgeI][0], edges[edgeI][1], edges[edgeI][2])
            edgeI += 1
        answer = hld.pathQuery(a, b)
        queryAnswers[queryI] = answer
    
    for v in queryAnswers:
        print(v)

    
t = int(input())
for _ in range(t):
    solve()