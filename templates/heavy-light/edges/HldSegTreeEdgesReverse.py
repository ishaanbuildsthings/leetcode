# =============================================================================
# 0-INDEXED HLD WITH EDGE-WEIGHTED VARIANT, NON-COMMUTATIVE COMBINE
# =============================================================================
# N = number of nodes, root is node 0
# edges = [(a, b, edgeVal), ...] where edgeVal is the edge's value
# base(val) -> stored data
# combine(data1, data2) -> aggregated data (NON-commutative; data1 is to the LEFT of data2 on the path)
# reverse(data) -> data as if the underlying segment were reversed (for non-commutative path queries)
# example
# def reverseData(d):
#     length, B, prefW, sufW, ww, badT = d
#     return (length, B, sufW, prefW, ww, badT)
#
# Each edge's value is pushed onto its DEEPER endpoint (the child).
# The root has no edge above it, so its slot is unused (None).
#
#
# METHODS
# -------
# pointSet(node, newEdgeVal)
#   Sets the value of the edge ABOVE `node`. No-op if node is the root.
#   Takes in the RAW edge data, so for instance a letter if edges have letters
#
# pointApply(node, delta)
#   Applies delta to the edge above `node` via combine.
#   E.g. for XOR: existing ^ delta. For sum: existing + delta. No-op if root.
#
# edgeSet(a, b, newEdgeVal)
#   Sets the value of the edge between adjacent nodes a and b.
#   a and b MUST be adjacent (one is parent of the other).
#   Takes in the RAW edge value so for instance a letter if edges have letters
#
# edgeApply(a, b, delta)
#   Applies delta to the edge between adjacent nodes a and b.
#
# pathQuery(a, b) -> EdgeData
#   Aggregated data over the EDGES on path a..b, in path order from a to b.
#   CALLER MUST ENSURE a != b (empty path returns None).
#
# subtreeQuery(node) -> EdgeData
#   Aggregated data over edges from node down to all its descendants, in DFS order.
#   The edge ABOVE node itself is NOT included.
#   CALLER MUST ENSURE node has at least one descendant (leaf returns None).
#
#
# EXAMPLE: path concatenation over edge labels
# --------------------------------------------
#   def base(v):
#       return v  # e.g. a single character
#   def combine(a, b):
#       return a + b
#   def reverseData(d):
#       return d[::-1]
#
#   # edges shape: each entry is (nodeA, nodeB, raw edge data)
#   edges = [
#       (0, 1, 'a'),
#       (1, 2, 'b'),
#       (0, 3, 'c'),
#   ]
#
#   hld = HLDEdge(n, edges, base, combine, reverseData)
#
#   answer = hld.pathQuery(2, 3)
#   print(answer)
# =============================================================================

class HLDEdge:
    def __init__(self, n, edges, base, combine, reverse):
        self.n = n
        self.base = base
        self.combine = combine
        self.reverse = reverse
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
        # combined data over [ql, qr] in DFS-position order (left-to-right)
        if ql > qr: return None
        resL = None
        resR = None
        ql += self.segN
        qr += self.segN + 1
        while ql < qr:
            if ql & 1:
                resL = self._combineOpt(resL, self.seg[ql])
                ql += 1
            if qr & 1:
                qr -= 1
                resR = self._combineOpt(self.seg[qr], resR)
            ql >>= 1
            qr >>= 1
        return self._combineOpt(resL, resR)

    # Non-commutative path query over EDGES.
    # Each chain segment from seg comes in DFS order (chain top first, chain bottom last).
    # Path a -> LCA -> b. Collect chunks in path order:
    #   leftPieces: from a moving up, each chunk reversed so it reads "deep first" (a-side)
    #   rightPieces: from b moving up, each chunk reversed so it reads "deep first" (b-side)
    # The LCA's own slot is SKIPPED (it represents the edge ABOVE the LCA, not on the path).
    # Final answer: combine(leftAcc, rightAcc) where rightAcc is built from b inward to LCA,
    # then reversed piece-by-piece so it reads LCA-side first.
    # Caller must ensure a != b.
    def pathQuery(self, a, b):
        leftPieces = []
        rightPieces = []
        while self.head[a] != self.head[b]:
            if self.depth[self.head[a]] >= self.depth[self.head[b]]:
                chunk = self._rangeQuery(self.pos[self.head[a]], self.pos[a])
                leftPieces.append(self.reverse(chunk))
                a = self.par[self.head[a]]
            else:
                chunk = self._rangeQuery(self.pos[self.head[b]], self.pos[b])
                rightPieces.append(self.reverse(chunk))
                b = self.par[self.head[b]]
        if self.depth[a] >= self.depth[b]:
            # b is the LCA (or a == b); skip its slot by querying [pos[b]+1, pos[a]]
            chunk = self._rangeQuery(self.pos[b] + 1, self.pos[a])
            if chunk is not None:
                leftPieces.append(self.reverse(chunk))
        else:
            # a is the LCA; skip its slot by querying [pos[a]+1, pos[b]]
            chunk = self._rangeQuery(self.pos[a] + 1, self.pos[b])
            if chunk is not None:
                rightPieces.append(self.reverse(chunk))
        leftAcc = None
        for p in leftPieces:
            leftAcc = p if leftAcc is None else self.combine(leftAcc, p)
        rightAcc = None
        for p in reversed(rightPieces):
            rev = self.reverse(p)
            rightAcc = rev if rightAcc is None else self.combine(rightAcc, rev)
        if leftAcc is None: return rightAcc
        if rightAcc is None: return leftAcc
        return self.combine(leftAcc, rightAcc)

    # subtree edge query: edges from node down to all its descendants
    # = all stored slots in subtree EXCEPT node's own (which is the edge above node, not in subtree)
    # Caller must ensure node has at least one descendant (else returns None).
    def subtreeQuery(self, node):
        return self._rangeQuery(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1)
