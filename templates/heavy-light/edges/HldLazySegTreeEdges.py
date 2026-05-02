# =============================================================================
# 0-INDEXED HLD WITH EDGE-WEIGHTED VARIANT, LAZY PROPAGATION
# =============================================================================
# N = number of nodes, root is node 0
# edges = [(a, b, edgeVal), ...] where edgeVal is the edge's value
# base(rawVal) -> stored data
# combine(data1, data2) -> aggregated data
# applyLazy(lazy, data, segLen) -> data after applying lazy over segLen positions
#   segLen is # of underlying positions covered by data, I just exposed it here
# composeLazies(oldLazy, newLazy) -> combined lazy
#
# Each edge's value is pushed onto its DEEPER endpoint (the child).
# The root has no edge above it, so its slot is unused (None).
# Path/subtree updates and queries always SKIP the relevant LCA / root slot,
# so applyLazy is never invoked on a None data slot.
#
#
# METHODS
# -------
# pointSet(node, newEdgeVal)
#   Sets the value of the edge ABOVE `node`. No-op if node is the root.
#   Takes in the RAW edge data, so for instance a letter if edges have letters
#
# pointApply(node, lazyVal)
#   Applies lazyVal to the edge above `node`. No-op if node is the root.
#
# edgeSet(a, b, newEdgeVal)
#   Sets the value of the edge between adjacent nodes a and b.
#   a and b MUST be adjacent (one is parent of the other).
#
# edgeApply(a, b, lazyVal)
#   Applies lazyVal to the edge between adjacent nodes a and b.
#
# pathApply(a, b, lazyVal)
#   Applies lazyVal to all EDGES on path a..b. No-op if a == b.
#
# subtreeApply(node, lazyVal)
#   Applies lazyVal to all edges from node down to all its descendants.
#   The edge ABOVE node itself is NOT touched.
#
# pathQuery(a, b) -> EdgeData
#   Aggregated data over the EDGES on path a..b.
#   CALLER MUST ENSURE a != b (empty path returns None).
#
# subtreeQuery(node) -> EdgeData
#   Aggregated data over edges from node down to all its descendants.
#   The edge ABOVE node itself is NOT included.
#   CALLER MUST ENSURE node has at least one descendant (leaf returns None).
#
# we don't need a baseLazy() or anything like that, because initially all lazy tags are None,
# and if we apply a lazy to that it just uses the new lazy entirely
#
#
# EXAMPLE: path sum over edge weights with range-add updates
# ----------------------------------------------------------
#   def base(v):
#       return v
#   def combine(a, b):
#       return a + b
#   def applyLazy(lz, d, segLen):
#       return d + lz * segLen   # add lz to each position; sum shifts by lz * segLen
#   def composeLazies(oldL, newL):
#       return oldL + newL
#
#   edges = [
#       (0, 1, 5),
#       (1, 2, 3),
#       (0, 3, 7),
#   ]
#
#   hld = LazyHLDEdge(n, edges, base, combine, applyLazy, composeLazies)
#   hld.pathApply(2, 3, 10)                # add 10 to every edge on path 2..3
#   total = hld.pathQuery(2, 3)
# =============================================================================

class LazyHLDEdge:
    def __init__(self, n, edges, base, combine, applyLazy, composeLazies):
        self.n = n
        self.base = base
        self.combine = combine
        self.applyLazy = applyLazy
        self.composeLazies = composeLazies
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
        while self.segN < max(n, 1):
            self.segN <<= 1
        self.LOG = max(1, self.segN.bit_length() - 1)
        self.tree = [None] * (2 * self.segN)
        self.lazy = [None] * self.segN
        for i in range(n):
            if self.edgeAbove[i] is not None:
                self.tree[self.segN + self.pos[i]] = base(self.edgeAbove[i])
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

    def pointSet(self, node, newEdgeVal):
        if node == 0: return  # root has no edge above
        self._segPointSet(self.pos[node], self.base(newEdgeVal))

    def pointApply(self, node, lazyVal):
        if node == 0: return
        p = self.pos[node]
        self._segUpdate(p, p, lazyVal)

    # a and b must be adjacent in the tree; the deeper one is the child whose slot stores this edge
    def edgeSet(self, a, b, newEdgeVal):
        child = a if self.depth[a] > self.depth[b] else b
        self.pointSet(child, newEdgeVal)

    def edgeApply(self, a, b, lazyVal):
        child = a if self.depth[a] > self.depth[b] else b
        self.pointApply(child, lazyVal)

    def pathApply(self, a, b, lazyVal):
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] < self.depth[self.head[b]]:
                a, b = b, a
            self._segUpdate(self.pos[self.head[a]], self.pos[a], lazyVal)
            a = self.par[self.head[a]]
        if self.depth[a] > self.depth[b]:
            a, b = b, a
        # a is the LCA; skip its slot by updating [pos[a]+1, pos[b]]
        self._segUpdate(self.pos[a] + 1, self.pos[b], lazyVal)

    def subtreeApply(self, node, lazyVal):
        self._segUpdate(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1, lazyVal)

    # Path query over EDGES from a to b. Skips the LCA's slot since that represents
    # the edge ABOVE the LCA, which is not on the a-b path.
    # Caller must ensure a != b (else returns None).
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
        last = self._segQuery(self.pos[a] + 1, self.pos[b])
        return self._combineOpt(res, last)

    # subtree edge query: edges from node down to all its descendants
    # = all stored slots in subtree EXCEPT node's own (which is the edge above node, not in subtree)
    # Caller must ensure node has at least one descendant (else returns None).
    def subtreeQuery(self, node):
        return self._segQuery(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1)
