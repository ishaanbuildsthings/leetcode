# 0-INDEXED, ALL INTERFACES OPERATION ON 0-indexed data
# N = number of nodes
# edges = [a, b], [c, d], ...
# vals[node] -> value, like a letter or number
# base(nodeValue) -> stored data
# combine(node1data, node2data) -> aggregate data

# pointSet(node, newValue) like a new letter
# pointApply(node, delta) adds +delta (used if we stored sums)
# pathQuery(a, b) -> gives us aggregated data
# subtreeQuery(a) -> gives us subtree data for that

# hld = HLD(numNodes, edgeList, vals, baseFn, combineFn)
class HLD:
    def __init__(self, n, edges, vals, base, combine):
        self.n = n
        self.base = base
        self.combine = combine
        self.adj = [[] for _ in range(n)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.par = [-1] * n
        self.depth = [0] * n
        self.sz = [1] * n
        self.heavy = [-1] * n
        self.head = [0] * n
        self.pos = [0] * n
        self._dfsInit()
        self._dfsDecompose()
        # build seg tree
        self.segN = 1
        while self.segN < n:
            self.segN <<= 1
        self.seg = [None] * (2 * self.segN)
        for i in range(n):
            self.seg[self.segN + self.pos[i]] = base(vals[i])
        for i in range(self.segN - 1, 0, -1):
            self.seg[i] = self._combineOpt(self.seg[2*i], self.seg[2*i+1])
    
    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)
    
    def _dfsInit(self):
        # iterative, compute sz, par, depth, heavy
        order = []
        stack = [(0, -1, 0)]
        while stack:
            node, parent, d = stack.pop()
            self.par[node] = parent
            self.depth[node] = d
            order.append(node)
            for nxt in self.adj[node]:
                if nxt != parent:
                    stack.append((nxt, node, d + 1))
        # process in reverse order to compute sz and heavy
        for node in reversed(order):
            best = 0
            for nxt in self.adj[node]:
                if nxt == self.par[node]: continue
                self.sz[node] += self.sz[nxt]
                if self.sz[nxt] > best:
                    best = self.sz[nxt]
                    self.heavy[node] = nxt
    
    def _dfsDecompose(self):
        timer = 0
        stack = [(0, 0)] # (node, chainHead)
        while stack:
            node, h = stack.pop()
            self.head[node] = h
            self.pos[node] = timer
            timer += 1
            # push light children first so they're processed AFTER heavy
            for nxt in self.adj[node]:
                if nxt == self.par[node] or nxt == self.heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if self.heavy[node] != -1:
                stack.append((self.heavy[node], h))
    
    def pointSet(self, node, rawVal):
        p = self.pos[node] + self.segN
        self.seg[p] = self.base(rawVal)
        p >>= 1
        while p:
            self.seg[p] = self._combineOpt(self.seg[2*p], self.seg[2*p+1])
            p >>= 1
    
    def pointApply(self, node, rawDelta):
        p = self.pos[node] + self.segN
        self.seg[p] = self._combineOpt(self.seg[p], self.base(rawDelta))
        p >>= 1
        while p:
            self.seg[p] = self._combineOpt(self.seg[2*p], self.seg[2*p+1])
            p >>= 1
    
    def _rangeQuery(self, ql, qr):
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
        last = self._rangeQuery(self.pos[a], self.pos[b])
        return self._combineOpt(res, last)
    
    def subtreeQuery(self, node):
        return self._rangeQuery(self.pos[node], self.pos[node] + self.sz[node] - 1)