# EXAMPLE
#
# TYPES:
# EdgeData (usually a tuple or normal number)
#
# here EdgeData is a tuple (total, pref, suf, best, length) for max subsegment sum

# def base(rawVal) -> EdgeData:
#     return (rawVal, rawVal, rawVal, rawVal, 1)

# how to aggregate two EdgeData nodes, order matters
# def mergeFn(EdgeData1, EdgeData2) -> EdgeData:
#     at, ap, asf, ab, al = EdgeData1
#     bt, bp, bsf, bb, bl = EdgeData2
#     return (at + bt, max(ap, at + bp), max(bsf, bt + asf), max(ab, bb, asf + bp), al + bl)

# how to reverse an EdgeData
# def reverseFn(edgeData) -> EdgeData:
#     total, pref, suf, best, length = edgeData
#     return (total, suf, pref, best, length)


# TO CREATE THE HLD (O(n) build time)
# edges should be [(a, b), (c, d), ...]
# vals[node] is the edge ABOVE that node, if we are using root=1, then vals[0] can be whatever dummy value
# root can be any node in the tree, separate from if the nodes are 0..n-1 or 1..n
# last param is `zeroIndexed`, so False means the nodes are 1..n
# hld = HldSegTreeEdgesReverse(edges, vals, base, mergeFn, reverseFn, 1, False)


# METHODS

# O(logN)
# pointSet(nodeLabel, RawEdgeVal), overwrites the edge above `nodeLabel` with this new raw value

# O(logN)
# pointApply(nodeLabel, RawEdgeVal), combines this raw value into the edge above `nodeLabel`

# O(log^2 N)
# pathQuery(a, b) -> EdgeData, gives us the aggregated data on the path a->b, returns None if a==b

# O(log N)
# subtreeQuery(nodeLabel) -> EdgeData, aggregated data of all edges in the subtree (orientation is unspecified / not ordered), returns None if a leaf


class HldSegTreeEdgesReverse:
    def __init__(self, edges, vals, base, combine, reverse, root, zeroIndexed):
        n = len(edges) + 1
        self.n = n
        self.root = root
        self.zeroIndexed = zeroIndexed
        self.base = base
        self.combine = combine
        self.reverse = reverse
        arrSize = n if zeroIndexed else n + 1
        self.adj = [[] for _ in range(arrSize)]
        for u, v in edges:
            self.adj[u].append(v)
            self.adj[v].append(u)
        self.par = [-1] * arrSize
        self.depth = [0] * arrSize
        self.sz = [1] * arrSize
        self.heavy = [-1] * arrSize
        self.head = [0] * arrSize
        self.pos = [0] * arrSize
        self._dfsInit()
        self._dfsDecompose()
        segN = 1
        while segN < max(n, 1):
            segN <<= 1
        self.segN = segN
        self.tree = [None] * (2 * segN)
        lo = 0 if zeroIndexed else 1
        hi = n if zeroIndexed else n + 1
        for i in range(lo, hi):
            if i != root:
                self.tree[segN + self.pos[i]] = base(vals[i])
        for i in range(segN - 1, 0, -1):
            self.tree[i] = self._combineOpt(self.tree[2*i], self.tree[2*i+1])

    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)

    def _reverseOpt(self, a):
        if a is None: return a
        return self.reverse(a)

    def _dfsInit(self):
        adj, par, depth, sz, heavy = self.adj, self.par, self.depth, self.sz, self.heavy
        order = []
        stack = [(self.root, -1, 0)]
        while stack:
            node, parent, d = stack.pop()
            par[node] = parent
            depth[node] = d
            order.append(node)
            for nxt in adj[node]:
                if nxt != parent:
                    stack.append((nxt, node, d + 1))
        for node in reversed(order):
            best = 0
            for nxt in adj[node]:
                if nxt == par[node]:
                    continue
                sz[node] += sz[nxt]
                if sz[nxt] > best:
                    best = sz[nxt]
                    heavy[node] = nxt

    def _dfsDecompose(self):
        adj, par, heavy, head, pos = self.adj, self.par, self.heavy, self.head, self.pos
        timer = 0
        stack = [(self.root, self.root)]
        while stack:
            node, h = stack.pop()
            head[node] = h
            pos[node] = timer
            timer += 1
            for nxt in adj[node]:
                if nxt == par[node] or nxt == heavy[node]:
                    continue
                stack.append((nxt, nxt))
            if heavy[node] != -1:
                stack.append((heavy[node], h))

    def _segQuery(self, l, r):
        if l > r:
            return None
        segN = self.segN
        tree = self.tree
        l += segN
        r += segN + 1
        resL = None
        resR = None
        while l < r:
            if l & 1:
                resL = self._combineOpt(resL, tree[l]); l += 1
            if r & 1:
                r -= 1; resR = self._combineOpt(tree[r], resR)
            l >>= 1; r >>= 1
        return self._combineOpt(resL, resR)

    def _segPointSet(self, idx, newData):
        tree = self.tree
        p = idx + self.segN
        tree[p] = newData
        p >>= 1
        while p:
            tree[p] = self._combineOpt(tree[2*p], tree[2*p+1])
            p >>= 1

    def pointSet(self, node, rawVal):
        self._segPointSet(self.pos[node], self.base(rawVal))

    def pointApply(self, node, rawVal):
        p = self.pos[node] + self.segN
        self._segPointSet(self.pos[node], self._combineOpt(self.tree[p], self.base(rawVal)))

    # ORDERED path query a -> b. returns None if a == b.
    # Each _segQuery chunk is stored ancestor->descendant (pos-increasing). We split the
    # path at the LCA and accumulate the two sides separately. As we climb, each newly
    # fetched chunk is higher up, so we PREPEND it to keep each side ordered top->bottom
    # (ancestor->descendant). The b-side in that orientation is already the correct forward
    # order (lca->b). The a-side's real traversal is a->lca, i.e. bottom->top, the reverse
    # of how it's stored, so we reverse it before joining.
    def pathQuery(self, a, b):
        head, depth, par, pos = self.head, self.depth, self.par, self.pos
        accA = None  # a-side edges, stored ancestor->descendant
        accB = None  # b-side edges, stored ancestor->descendant
        ca, cb = a, b
        while head[ca] != head[cb]:
            if depth[head[ca]] > depth[head[cb]]:
                accA = self._combineOpt(self._segQuery(pos[head[ca]], pos[ca]), accA)
                ca = par[head[ca]]
            else:
                accB = self._combineOpt(self._segQuery(pos[head[cb]], pos[cb]), accB)
                cb = par[head[cb]]
        if depth[ca] > depth[cb]:
            accA = self._combineOpt(self._segQuery(pos[cb] + 1, pos[ca]), accA)
        elif depth[cb] > depth[ca]:
            accB = self._combineOpt(self._segQuery(pos[ca] + 1, pos[cb]), accB)
        return self._combineOpt(self._reverseOpt(accA), accB)

    # returns None if node is a leaf
    def subtreeQuery(self, node):
        return self._segQuery(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1)