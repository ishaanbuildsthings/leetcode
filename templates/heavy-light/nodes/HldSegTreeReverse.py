# 0-INDEXED, ALL INTERFACES OPERATION ON 0-indexed data
# N = number of nodes
# edges = [a, b], [c, d], ...
# vals[node] -> value, like a letter or number
# base(nodeValue) -> stored data
# combine(node1data, node2data) -> aggregate data (NON-commutative; node1 is to the LEFT of node2 on the path)
# reverse(data) -> data as if the underlying segment were reversed (for non-commutative path queries)
# example
# def reverseData(d):
#     length, B, prefW, sufW, ww, badT = d
#     return (length, B, sufW, prefW, ww, badT)

# pointSet(node, newValue) like a new letter
# pointApply(node, delta) applies a delta to a node, such as an XOR or add
# pathQuery(a, b) -> gives us aggregated data
# subtreeQuery(a) -> gives us subtree data for that

# hld = HLD(numNodes, edgeList, vals, baseFn, combineFn, reverseFn)
class HLD:
    def __init__(self, n, edges, vals, base, combine, reverse):
        self.n = n
        self.base = base
        self.combine = combine
        self.reverse = reverse
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
        # combined data over [ql, qr] in DFS-position order (left-to-right)
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
    
    # Non-commutative path query.
    # Each chain segment from seg comes in DFS order (chain top first, chain bottom last).
    # Path a -> LCA -> b. Collect chunks in path order:
    #   leftPieces: from a moving up, each chunk reversed so it reads "deep first" (a-side)
    #   rightPieces: from b moving up, each chunk reversed so it reads "deep first" (b-side)
    # Final answer: combine(leftAcc, rightAcc) where rightAcc is built from b inward to LCA,
    # then reversed piece-by-piece so it reads LCA-side first.
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
            chunk = self._rangeQuery(self.pos[b], self.pos[a])
            leftPieces.append(self.reverse(chunk))
        else:
            chunk = self._rangeQuery(self.pos[a], self.pos[b])
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
    
    def subtreeQuery(self, node):
        return self._rangeQuery(self.pos[node], self.pos[node] + self.sz[node] - 1)