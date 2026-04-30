# 0-INDEXED, ALL INTERFACES OPERATE ON 0-indexed data
# N = number of nodes
# edges = [a, b], [c, d], ...
# vals[node] -> raw value, like a letter or number
# base(rawVal) -> stored data (e.g. v -> (v, v) to track min and max)
# combine(data1, data2) -> aggregated data
# applyLazy(lazy, data, segLen) -> data after applying lazy over segLen positions
#   segLen is # of underlying positions covered by data, I just exposed it here
# composeLazies(oldLazy, newLazy) -> combined lazy

# pointSet(node, rawVal)
# pointApply(node, lazyVal)
# pathApply(a, b, lazyVal) — applies lazyVal to all nodes on path a..b
# subtreeApply(node, lazyVal) — applies lazyVal to entire subtree rooted at node
# pathQuery(a, b) -> aggregated data over path
# subtreeQuery(node) -> aggregated data over subtree
# we don't need a baseLazy() or anything like that, because initially all lazy tags are None, and if we apply a lazy to that it just uses the new lazy entirely

# hld = LazyHLD(numNodes, edgeList, vals, baseFn, combineFn, applyLazyFn, composeLaziesFn)
class LazyHLD:
    def __init__(self, n, edges, vals, base, combine, applyLazy, composeLazies):
        self.n = n
        self.base = base
        self.combine = combine
        self.applyLazy = applyLazy
        self.composeLazies = composeLazies
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
        self.segN = 1
        while self.segN < max(n, 1):
            self.segN <<= 1
        self.LOG = max(1, self.segN.bit_length() - 1)
        self.tree = [None] * (2 * self.segN)
        self.lazy = [None] * self.segN
        for i in range(n):
            self.tree[self.segN + self.pos[i]] = base(vals[i])
        for i in range(self.segN - 1, 0, -1):
            self.tree[i] = self._combineOpt(self.tree[2*i], self.tree[2*i+1])
    
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
            for nxt in self.adj[node]:
                if nxt != parent:
                    stack.append((nxt, node, d + 1))
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
        stack = [(0, 0)]
        while stack:
            node, h = stack.pop()
            self.head[node] = h
            self.pos[node] = timer
            timer += 1
            for nxt in self.adj[node]:
                if nxt == self.par[node] or nxt == self.heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if self.heavy[node] != -1:
                stack.append((self.heavy[node], h))
    
    def _segLenAt(self, p):
        return self.segN >> (p.bit_length() - 1)
    
    def _apply(self, p, lazyVal, segLen):
        self.tree[p] = self.applyLazy(lazyVal, self.tree[p], segLen)
        if p < self.segN:
            if self.lazy[p] is None:
                self.lazy[p] = lazyVal
            else:
                self.lazy[p] = self.composeLazies(self.lazy[p], lazyVal)
    
    def _push(self, p):
        if p < self.segN and self.lazy[p] is not None:
            childSegLen = self._segLenAt(2*p)
            self._apply(2*p, self.lazy[p], childSegLen)
            self._apply(2*p+1, self.lazy[p], childSegLen)
            self.lazy[p] = None
    
    def _pushTo(self, p):
        for s in range(self.LOG, 0, -1):
            self._push(p >> s)
    
    def _pullFrom(self, p):
        p >>= 1
        while p:
            newVal = self._combineOpt(self.tree[2*p], self.tree[2*p+1])
            if self.lazy[p] is not None:
                newVal = self.applyLazy(self.lazy[p], newVal, self._segLenAt(p))
            self.tree[p] = newVal
            p >>= 1
    
    def _segUpdate(self, l, r, lazyVal):
        if l > r: return
        l += self.segN
        r += self.segN + 1
        l0, r0 = l, r
        self._pushTo(l0)
        self._pushTo(r0 - 1)
        segLen = 1
        ll, rr = l, r
        while ll < rr:
            if ll & 1:
                self._apply(ll, lazyVal, segLen)
                ll += 1
            if rr & 1:
                rr -= 1
                self._apply(rr, lazyVal, segLen)
            ll >>= 1
            rr >>= 1
            segLen <<= 1
        self._pullFrom(l0)
        self._pullFrom(r0 - 1)
    
    def _segQuery(self, l, r):
        if l > r: return None
        l += self.segN
        r += self.segN + 1
        self._pushTo(l)
        self._pushTo(r - 1)
        resL = None
        resR = None
        while l < r:
            if l & 1:
                resL = self._combineOpt(resL, self.tree[l])
                l += 1
            if r & 1:
                r -= 1
                resR = self._combineOpt(self.tree[r], resR)
            l >>= 1
            r >>= 1
        return self._combineOpt(resL, resR)
    
    def _segPointSet(self, idx, newData):
        p = idx + self.segN
        self._pushTo(p)
        self.tree[p] = newData
        p >>= 1
        while p:
            newVal = self._combineOpt(self.tree[2*p], self.tree[2*p+1])
            if self.lazy[p] is not None:
                newVal = self.applyLazy(self.lazy[p], newVal, self._segLenAt(p))
            self.tree[p] = newVal
            p >>= 1
    
    def pointSet(self, node, rawVal):
        self._segPointSet(self.pos[node], self.base(rawVal))
    
    def pointApply(self, node, lazyVal):
        p = self.pos[node]
        self._segUpdate(p, p, lazyVal)
    
    def pathApply(self, a, b, lazyVal):
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] < self.depth[self.head[b]]:
                a, b = b, a
            self._segUpdate(self.pos[self.head[a]], self.pos[a], lazyVal)
            a = self.par[self.head[a]]
        if self.depth[a] > self.depth[b]:
            a, b = b, a
        self._segUpdate(self.pos[a], self.pos[b], lazyVal)
    
    def subtreeApply(self, node, lazyVal):
        self._segUpdate(self.pos[node], self.pos[node] + self.sz[node] - 1, lazyVal)
    
    def pathQuery(self, a, b):
        res = None
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] < self.depth[self.head[b]]:
                a, b = b, a
            chain = self._segQuery(self.pos[self.head[a]], self.pos[a])
            res = self._combineOpt(res, chain)
            a = self.par[self.head[a]]
        if self.depth[a] > self.depth[b]:
            a, b = b, a
        last = self._segQuery(self.pos[a], self.pos[b])
        return self._combineOpt(res, last)
    
    def subtreeQuery(self, node):
        return self._segQuery(self.pos[node], self.pos[node] + self.sz[node] - 1)