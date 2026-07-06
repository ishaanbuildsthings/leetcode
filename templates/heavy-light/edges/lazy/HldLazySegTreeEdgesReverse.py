# EXAMPLE
#
# TYPES:
# EdgeData (usually a tuple or normal number)
# LazyTag (also usually a normal number, tuple, etc)
#
# here EdgeData is a tuple (total, pref, suf, best, length) for max subsegment sum

# def base(rawVal) -> EdgeData:
#     return (rawVal, rawVal, rawVal, rawVal, 1)

# how to aggregate two EdgeData nodes, order matters
# def mergeFn(EdgeData1, EdgeData2) -> EdgeData:
#     at, ap, asf, ab, al = EdgeData1
#     bt, bp, bsf, bb, bl = EdgeData2
#     return (at + bt, max(ap, at + bp), max(bsf, bt + asf), max(ab, bb, asf + bp), al + bl)

# how to apply a lazy update to EdgeData
# def applyLazy(LazyTag, edgeData) -> EdgeData:
#     total, pref, suf, best, length = edgeData
#     whole = lazy * length
#     one = max(lazy, whole)
#     return (whole, one, one, one, length)

# how to combine two lazies
# def composeLazies(LazyTag1, LazyTag2) -> LazyTag:
#     return b

# how to reverse an EdgeData
# def reverseFn(edgeData) -> EdgeData:
#     total, pref, suf, best, length = edgeData
#     return (total, suf, pref, best, length)


# TO CREATE THE HLD (O(n) build time)
# edges should be [(a, b), (c, d), ...]
# vals[node] is the edge ABOVE that node, if we are using root=1, then vals[0] can be whatever dummy value
# root can be any node in the tree, separate from if the nodes are 0..n-1 or 1..n
# last param is `zeroIndexed`, so False means the nodes are 1..n
# hld = HldLazySegTreeEdgesReverse(edges, vals, base, mergeFn, applyLazy, composeLazies, reverseFn, 1, False)


# METHODS

# O(logN)
# pointSet(nodeLabel, RawEdgeVal), overwrites the edge above `nodeLabel` with this new raw value

# O(logN)
# pointApply(nodeLabel, lazyVal), directly apply a lazy update to the edge above `nodeLabel`

# O(log^2 N)
# pathApply(a, b, lazyVal), applies this lazy update to the entire path a..b, not an ordered update or anything, since the same lazyVal is just going on the whole path

# O(log^2 N)
# pathQuery(a, b) -> EdgeData, gives us the aggregated data on the path a->b, returns None if a==b

# O(log N)
# subtreeApply(nodeLabel, lazyVal), applies this update to all edges in the subtree of nodeLabel, no-op if a leaf

# O(log N)
# subtreeQuery(nodeLabel) -> EdgeData, aggregated data of all edges in the subtree (orientation is unspecified / not ordered), returns None if a leaf


class HldLazySegTreeEdgesReverse:
    def __init__(self, edges, vals, base, combine, applyLazy, composeLazies, reverse, root, zeroIndexed):
        n = len(edges) + 1
        self.n = n
        self.root = root
        self.zeroIndexed = zeroIndexed
        self.base = base
        self.combine = combine
        self.applyLazy = applyLazy
        self.composeLazies = composeLazies
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
        self.LOG = max(1, segN.bit_length() - 1)
        self.tree = [None] * (2 * segN)
        self.lazy = [None] * segN
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

    def _apply(self, p, lazyVal):
        tree = self.tree
        if tree[p] is None:
            return
        tree[p] = self.applyLazy(lazyVal, tree[p])
        if p < self.segN:
            lz = self.lazy
            lz[p] = lazyVal if lz[p] is None else self.composeLazies(lz[p], lazyVal)

    def _pushTo(self, p):
        tree, lazy, segN = self.tree, self.lazy, self.segN
        applyLazy, composeLazies = self.applyLazy, self.composeLazies
        for s in range(self.LOG, 0, -1):
            q = p >> s
            lz = lazy[q]
            if lz is not None:
                for c in (2*q, 2*q+1):
                    if tree[c] is not None:
                        tree[c] = applyLazy(lz, tree[c])
                    if c < segN:
                        lazy[c] = lz if lazy[c] is None else composeLazies(lazy[c], lz)
                lazy[q] = None

    def _pullFrom(self, p):
        tree, lazy = self.tree, self.lazy
        combine, applyLazy = self.combine, self.applyLazy
        p >>= 1
        while p:
            a = tree[2*p]; b = tree[2*p+1]
            if a is None:
                newVal = b
            elif b is None:
                newVal = a
            else:
                newVal = combine(a, b)
            lz = lazy[p]
            if lz is not None and newVal is not None:
                newVal = applyLazy(lz, newVal)
            tree[p] = newVal
            p >>= 1

    def _segUpdate(self, l, r, lazyVal):
        if l > r:
            return
        segN = self.segN
        l += segN
        r += segN + 1
        l0, r0 = l, r
        self._pushTo(l0)
        self._pushTo(r0 - 1)
        ll, rr = l, r
        while ll < rr:
            if ll & 1:
                self._apply(ll, lazyVal); ll += 1
            if rr & 1:
                rr -= 1; self._apply(rr, lazyVal)
            ll >>= 1; rr >>= 1
        self._pullFrom(l0)
        self._pullFrom(r0 - 1)

    def _segQuery(self, l, r):
        if l > r:
            return None
        segN = self.segN
        tree = self.tree
        combine = self.combine
        self._pushTo(l + segN)
        self._pushTo(r + segN)
        l += segN
        r += segN + 1
        resL = None
        resR = None
        while l < r:
            if l & 1:
                t = tree[l]
                if t is not None:
                    resL = t if resL is None else combine(resL, t)
                l += 1
            if r & 1:
                r -= 1
                t = tree[r]
                if t is not None:
                    resR = t if resR is None else combine(t, resR)
            l >>= 1; r >>= 1
        if resL is None: return resR
        if resR is None: return resL
        return combine(resL, resR)

    def _segPointSet(self, idx, newData):
        tree, lazy = self.tree, self.lazy
        combine, applyLazy = self.combine, self.applyLazy
        self._pushTo(idx + self.segN)
        p = idx + self.segN
        tree[p] = newData
        p >>= 1
        while p:
            a = tree[2*p]; b = tree[2*p+1]
            if a is None:
                newVal = b
            elif b is None:
                newVal = a
            else:
                newVal = combine(a, b)
            lz = lazy[p]
            if lz is not None and newVal is not None:
                newVal = applyLazy(lz, newVal)
            tree[p] = newVal
            p >>= 1

    def pointSet(self, node, rawVal):
        self._segPointSet(self.pos[node], self.base(rawVal))

    def pointApply(self, node, lazyVal):
        p = self.pos[node]
        self._segUpdate(p, p, lazyVal)

    def pathApply(self, a, b, lazyVal):
        head, depth, par, pos = self.head, self.depth, self.par, self.pos
        while head[a] != head[b]:
            if depth[head[a]] < depth[head[b]]:
                a, b = b, a
            self._segUpdate(pos[head[a]], pos[a], lazyVal)
            a = par[head[a]]
        if depth[a] > depth[b]:
            a, b = b, a
        if pos[a] + 1 <= pos[b]:
            self._segUpdate(pos[a] + 1, pos[b], lazyVal)

    def subtreeApply(self, node, lazyVal):
        if self.sz[node] > 1:
            self._segUpdate(self.pos[node] + 1, self.pos[node] + self.sz[node] - 1, lazyVal)

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