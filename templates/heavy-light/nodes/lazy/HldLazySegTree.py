# EXAMPLE
#
# TYPES:
# NodeData (usually a tuple or normal number)
# # LazyTag (also usually a normal number, tuple, etc)

# def base(rawVal) -> NodeData:
#     return rawVal
#
# how to aggregate two NodeData nodes
# def mergeFn(nodeData1, nodeData2) -> NodeData:
#     return nodeData1 + nodeData2

# how to apply a lazy update to NodeData
# def applyLazy(LazyTag, nodeData) -> NodeData:
#     return nodeData + lazy

# how to combine two lazies
# def composeLazies(LazyTag1, LazyTag2) -> LazyTag:
#     return LazyTag1 + LazyTag2


# TO CREATE THE HLD (O(n) build time)
# edges should be [(a, b), (c, d), ...]
# vals[node] is the value AT that node, if the nodes are 1..n then vals[0] can be whatever dummy value
# root can be any node in the tree, separate from if the nodes are 0..n-1 or 1..n
# last param is `zeroIndexed`, so False means the nodes are 1..n
# hld = HldLazySegTree(edges, vals, base, mergeFn, applyLazy, composeLazies, 1, False)


# METHODS

# O(logN)
# pointSet(nodeLabel, RawVal), overwrites the value at `nodeLabel` with this new raw value

# O(logN)
# pointApply(nodeLabel, lazyVal), directly apply a lazy update to `nodeLabel`

# O(log^2 N)
# pathApply(a, b, lazyVal), applies this lazy update to the entire path a..b

# O(log^2 N)
# pathQuery(a, b) -> NodeData, gives us the aggregated data on the path a..b, includes both endpoints

# O(log N)
# subtreeApply(nodeLabel, lazyVal), applies this update to all nodes in the subtree of nodeLabel, includes nodeLabel itself

# O(log N)
# subtreeQuery(nodeLabel) -> NodeData, aggregated data of all nodes in the subtree, includes nodeLabel itself


class HldLazySegTree:
    def __init__(self, edges, vals, base, combine, applyLazy, composeLazies, root, zeroIndexed):
        n = len(edges) + 1
        self.n = n
        self.root = root
        self.zeroIndexed = zeroIndexed
        self.base = base
        self.combine = combine
        self.applyLazy = applyLazy
        self.composeLazies = composeLazies
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
            self.tree[segN + self.pos[i]] = base(vals[i])
        for i in range(segN - 1, 0, -1):
            self.tree[i] = self._combineOpt(self.tree[2*i], self.tree[2*i+1])

    def _combineOpt(self, a, b):
        if a is None: return b
        if b is None: return a
        return self.combine(a, b)

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
        # push pending lazy down the root->p path; skip empty tags
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
        self._segUpdate(pos[a], pos[b], lazyVal)

    def subtreeApply(self, node, lazyVal):
        self._segUpdate(self.pos[node], self.pos[node] + self.sz[node] - 1, lazyVal)

    def pathQuery(self, a, b):
        head, depth, par, pos = self.head, self.depth, self.par, self.pos
        res = None
        while head[a] != head[b]:
            if depth[head[a]] < depth[head[b]]:
                a, b = b, a
            res = self._combineOpt(res, self._segQuery(pos[head[a]], pos[a]))
            a = par[head[a]]
        if depth[a] > depth[b]:
            a, b = b, a
        res = self._combineOpt(res, self._segQuery(pos[a], pos[b]))
        return res

    def subtreeQuery(self, node):
        return self._segQuery(self.pos[node], self.pos[node] + self.sz[node] - 1)