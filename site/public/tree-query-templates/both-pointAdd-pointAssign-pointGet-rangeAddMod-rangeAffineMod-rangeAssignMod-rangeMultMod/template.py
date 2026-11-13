# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeAddMod-rangeAffineMod-rangeAssignMod-rangeMultMod/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeGet edgePathAddMod edgePathAffineMod edgePathMultMod edgeSubtreeAddMod edgeSubtreeAffineMod edgeSubtreeMultMod isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeGet nodePathAddMod nodePathAffineMod nodePathMultMod nodeSubtreeAddMod nodeSubtreeAffineMod nodeSubtreeMultMod parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: lazy-seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)
#   edgeAssign: log(N)
#   edgeGet: log(N)
#   edgePathAddMod: log^2(N)
#   edgePathAffineMod: log^2(N)
#   edgePathMultMod: log^2(N)
#   edgeSubtreeAddMod: log(N)
#   edgeSubtreeAffineMod: log(N)
#   edgeSubtreeMultMod: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAdd: log(N)
#   nodeAssign: log(N)
#   nodeGet: log(N)
#   nodePathAddMod: log^2(N)
#   nodePathAffineMod: log^2(N)
#   nodePathMultMod: log^2(N)
#   nodeSubtreeAddMod: log(N)
#   nodeSubtreeAffineMod: log(N)
#   nodeSubtreeMultMod: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N
# @memory:
#   layout: 2n-iterative
#   node: val[2*N]
#   tags: M[2*N] K[2*N]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: each internal node holds one pending affine map x -> x * M + K (% MOD); val holds the leaf values

# Range add / assign / multiply / affine % MOD + point ops, no range aggregates. All indices 0-based, ranges inclusive.
# Every update is an affine map (m, k): x -> m * x + k (% MOD):
#   add v -> (1, v)    mult m -> (m, 0)    assign v -> (0, v)    affine (m, b) -> (m, b)
# Affine maps compose but not commutatively, so the paths to l and r are pushed before tagging.
# Values are kept in [0, mod);
class AffineTree:
    __slots__ = ("n", "M", "K", "val", "mod")

    # O(N)
    def __init__(self, arr, mod=10**9 + 7):
        self.mod = mod
        n = self.n = len(arr)
        self.M = [1] * n
        self.K = [0] * n
        self.val = [v % mod for v in arr]

    # apply (m, k) on top of whatever node x already holds
    def _apply(self, x, m, k):
        n, mod = self.n, self.mod
        if x >= n:
            val = self.val
            val[x - n] = (val[x - n] * m + k) % mod
        else:
            M, K = self.M, self.K
            M[x] = M[x] * m % mod
            K[x] = (K[x] * m + k) % mod

    # O(logN) -- push every pending map on leaf p's root-to-leaf path down to its children
    def _push(self, p):
        M, K = self.M, self.K
        apply = self._apply
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            m, k = M[x], K[x]
            if m != 1 or k:
                y = x << 1
                apply(y, m, k)
                apply(y | 1, m, k)
                M[x] = 1
                K[x] = 0

    def _update(self, l, r, m, k):
        n = self.n
        l += n
        r += n
        self._push(l)
        self._push(r)
        r += 1
        apply = self._apply
        while l < r:
            if l & 1:
                apply(l, m, k)
                l += 1
            if r & 1:
                r -= 1
                apply(r, m, k)
            l >>= 1
            r >>= 1

    # O(logN) -- a[i] = a[i] * mult + add (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAffineMod(self, l, r, mult, add):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAffineMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, mult % self.mod, add % self.mod)

    # O(logN) -- a[i] = a[i] * m (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeMultMod(self, l, r, m):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMultMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, m % self.mod, 0)

    # O(logN) -- a[i] += v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAddMod(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAddMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, 1, v % self.mod)

    # O(logN) -- a[i] = v (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssignMod(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssignMod: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, 0, v % self.mod)

    # O(logN) -- a[i], in [0, mod): apply ancestors' maps bottom-up (deeper tags are older); needs 0 <= i < n, else
    # IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        M, K, mod = self.M, self.K, self.mod
        v = self.val[i]
        p = (i + self.n) >> 1
        while p:
            v = (v * M[p] + K[p]) % mod
            p >>= 1
        return v

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        M, K = self.M, self.K
        apply = self._apply
        for x in range(1, self.n):
            m, k = M[x], K[x]
            if m != 1 or k:
                apply(2 * x, m, k)
                apply(2 * x + 1, m, k)
                M[x] = 1
                K[x] = 0
        return list(self.val)

    # O(logN) -- a[i] = v (% MOD); needs 0 <= i < n, else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        self.val[i] = v % self.mod

    # O(logN) -- a[i] += delta (% MOD); needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self._push(i + self.n)
        self.val[i] = (self.val[i] + delta) % self.mod


from bisect import bisect_left


# tree = Tree(edges, root, vals, mod)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
# mod: the modulus MOD (every value is kept in [0, MOD)).
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30], mod)       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30], mod)    # nodes 1..3, rooted at 1
#
# The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
# nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
# edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
# (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
# returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (AffineTree) sit
# over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower end's
# position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain it
# crosses.
class Tree:
    # O(n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
    def __init__(self, edges, root, vals, mod=10**9 + 7):
        n = len(edges) + 1
        lo = float("inf")
        for e in edges:
            if len(e) != 2 and len(e) != 3:
                raise ValueError(f"Tree: every edge needs 2 or 3 numbers, (a, b) or (a, b, w), got {e}")
            if e[0] < lo:
                lo = e[0]
            if e[1] < lo:
                lo = e[1]
        if not edges:
            lo = root
        if lo != 0 and lo != 1:
            raise ValueError(f"Tree: nodes must be labeled 0..n-1 or 1..n, but the smallest label is {lo}")
        hi = lo + n - 1
        if not lo <= root <= hi:
            raise ValueError(f"Tree: root must be one of the nodes {lo}..{hi}, got {root}")
        adj = [[] for _ in range(hi + 1)]
        for e in edges:
            a, b = e[0], e[1]
            if a > hi or b > hi:
                raise ValueError(f"Tree: {n - 1} edges means the nodes are {lo}..{hi}, got the edge ({a}, {b})")
            adj[a].append(b)
            adj[b].append(a)

        # parents and depths, top down (par is -2 until a node is reached)
        par = [-2] * (hi + 1)
        dep = [0] * (hi + 1)
        par[root] = -1
        bfs = [root]
        for v in bfs:
            d = dep[v] + 1
            for u in adj[v]:
                if par[u] == -2:
                    par[u] = v
                    dep[u] = d
                    bfs.append(u)
        if len(bfs) != n:
            raise ValueError("Tree: the edges do not form one tree (some node cannot be reached from root)")

        # subtree sizes bottom up, then each node's heavy child (the one with the biggest subtree)
        sz = [1] * (hi + 1)
        for i in range(n - 1, 0, -1):
            v = bfs[i]
            sz[par[v]] += sz[v]
        heavy = [-1] * (hi + 1)
        for i in range(1, n):
            v = bfs[i]
            p = par[v]
            if heavy[p] == -1 or sz[v] > sz[heavy[p]]:
                heavy[p] = v

        # positions: a preorder that always steps into the heavy child first, so a heavy chain is one stretch
        head = [0] * (hi + 1)  # the top node of each node's chain
        pos = [0] * (hi + 1)
        order = [0] * n  # order[pos[v]] = v
        head[root] = root
        stack = [root]
        t = 0
        while stack:
            v = stack.pop()
            pos[v] = t
            order[t] = v
            t += 1
            h = heavy[v]
            p = par[v]
            for u in adj[v]:
                if u != p and u != h:
                    head[u] = u
                    stack.append(u)
            if h != -1:  # pushed last, so it is popped next
                head[h] = head[v]
                stack.append(h)

        # depthPos[depthStart[d] : depthStart[d + 1]] = the positions of the nodes at depth d, increasing
        maxDep = dep[bfs[-1]]
        depthStart = [0] * (maxDep + 2)
        for v in bfs:
            depthStart[dep[v] + 1] += 1
        for d in range(maxDep + 1):
            depthStart[d + 1] += depthStart[d]
        at = depthStart[:]
        depthPos = [0] * n
        for i in range(n):
            d = dep[order[i]]
            depthPos[at[d]] = i
            at[d] += 1

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos
        if len(vals) != hi + 1:
            raise ValueError(f"Tree: vals[node] is node's value, so nodes {lo}..{hi} need len(vals) = {hi + 1}"
                             f"{' (vals[0] is ignored)' if lo else ''}, got {len(vals)}")
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        arr = [edges[0][2] if edges else 0] * n  # (position 0 is the root's: it holds no edge, never read)
        for e in edges:
            a, b = e[0], e[1]
            arr[pos[a] if par[a] == b else pos[b]] = e[2]
        self.nodeSeg = AffineTree([vals[v] for v in order], mod)  # the node values, in position order
        self.edgeSeg = AffineTree(arr, mod)  # each edge's weight, at its lower end's position
        self.mod = mod

    # O(log n) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(log n) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.nodeSeg.pointAssign(self.pos[node], x)

    # O(log n) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.nodeSeg.pointAdd(self.pos[node], x)

    # O(log^2 n) -- val = (val + x) % MOD for every node on the path a..b
    def nodePathAddMod(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAddMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeAddMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, x) if l <= r else apply(r, l, x)

    # O(log^2 n) -- val = (val * m) % MOD for every node on the path a..b
    def nodePathMultMod(self, a, b, m):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMultMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeMultMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], m)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, m) if l <= r else apply(r, l, m)

    # O(log^2 n) -- val = (val * mult + add) % MOD for every node on the path a..b
    def nodePathAffineMod(self, a, b, mult, add):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAffineMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeAffineMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], mult, add)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, mult, add) if l <= r else apply(r, l, mult, add)

    # O(log n) -- val = (val + x) % MOD for every node in node's subtree
    def nodeSubtreeAddMod(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAddMod", node)
        l = self.pos[node]
        self.nodeSeg.rangeAddMod(l, l + self.sz[node] - 1, x)

    # O(log n) -- val = (val * m) % MOD for every node in node's subtree
    def nodeSubtreeMultMod(self, node, m):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMultMod", node)
        l = self.pos[node]
        self.nodeSeg.rangeMultMod(l, l + self.sz[node] - 1, m)

    # O(log n) -- val = (val * mult + add) % MOD for every node in node's subtree
    def nodeSubtreeAffineMod(self, node, mult, add):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAffineMod", node)
        l = self.pos[node]
        self.nodeSeg.rangeAffineMod(l, l + self.sz[node] - 1, mult, add)

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.edgeSeg.pointGet(self._edge("edgeGet", a, b))

    # O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.edgeSeg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        self.edgeSeg.pointAdd(self._edge("edgeAdd", a, b), w)

    # O(log^2 n) -- weight = (weight + w) % MOD for every edge on the path a..b
    def edgePathAddMod(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAddMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeAddMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], w)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, w) if l < r else apply(r + 1, l, w)

    # O(log^2 n) -- weight = (weight * m) % MOD for every edge on the path a..b
    def edgePathMultMod(self, a, b, m):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMultMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeMultMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], m)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, m) if l < r else apply(r + 1, l, m)

    # O(log^2 n) -- weight = (weight * mult + add) % MOD for every edge on the path a..b
    def edgePathAffineMod(self, a, b, mult, add):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAffineMod", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeAffineMod
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], mult, add)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, mult, add) if l < r else apply(r + 1, l, mult, add)

    # O(log n) -- weight = (weight + w) % MOD for every edge in node's subtree
    def edgeSubtreeAddMod(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAddMod", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.edgeSeg.rangeAddMod(l, r, w)

    # O(log n) -- weight = (weight * m) % MOD for every edge in node's subtree
    def edgeSubtreeMultMod(self, node, m):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeMultMod", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.edgeSeg.rangeMultMod(l, r, m)

    # O(log n) -- weight = (weight * mult + add) % MOD for every edge in node's subtree
    def edgeSubtreeAffineMod(self, node, mult, add):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAffineMod", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.edgeSeg.rangeAffineMod(l, r, mult, add)

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        head, par, dep = self.head, self.par, self.dep
        while head[a] != head[b]:
            if dep[head[a]] > dep[head[b]]:
                a = par[head[a]]
            else:
                b = par[head[b]]
        return a if dep[a] < dep[b] else b

    # the node k steps above node (k <= its depth): a whole chain at a time
    def _kth(self, node, k):
        head, pos, par = self.head, self.pos, self.par
        while True:
            h = head[node]
            d = pos[node] - pos[h]
            if k <= d:
                return self.order[pos[node] - k]
            k -= d + 1
            node = par[h]

    def _dist(self, a, b):
        dep = self.dep
        return dep[a] + dep[b] - 2 * dep[self._lca(a, b)]

    # of the three pairwise lcas two are equal and the third, the deeper one, is the median
    def _median(self, a, b, c):
        dep = self.dep
        x, y, z = self._lca(a, b), self._lca(a, c), self._lca(b, c)
        if dep[y] > dep[x]:
            x = y
        return z if dep[z] > dep[x] else x

    def _isAncestor(self, a, b):
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    def _onPath(self, a, b, node):
        return self._isAncestor(self._lca(a, b), node) and (self._isAncestor(node, a) or self._isAncestor(node, b))

    # the neighbor of a on the way to b (a != b): the child holding b when b is below a, else a's parent
    def _next(self, a, b):
        if self._isAncestor(a, b):
            return self._kth(b, self.dep[b] - self.dep[a] - 1)
        return self.par[a]

    # O(log n) -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # O(log n) -- number of edges on the path a..b
    def unweightedDist(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("unweightedDist", a, b)
        return self.dep[a] + self.dep[b] - 2 * self.dep[self._lca(a, b)]

    # O(1) -- edges from the root to node (the root is depth 0)
    def depth(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("depth", node)
        return self.dep[node]

    # O(1) -- node's parent (-1 for the root)
    def parent(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("parent", node)
        return self.par[node]

    # O(log n) -- the node k steps above node (k = 0 is node itself; -1 if that is past the root); needs k >= 0
    def kthAncestor(self, node, k):
        if not self.lo <= node <= self.hi:
            self._bad("kthAncestor", node)
        if k < 0:
            raise IndexError(f"kthAncestor: needs k >= 0, got {k}")
        return self._kth(node, k) if k <= self.dep[node] else -1

    # O(1) -- is a an ancestor of b? (True when a == b)
    def isAncestor(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("isAncestor", a, b)
        return self.pos[a] <= self.pos[b] < self.pos[a] + self.sz[a]

    # O(1) -- number of nodes in node's subtree (node included)
    def subtreeSize(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("subtreeSize", node)
        return self.sz[node]

    # O(log n) -- number of nodes in node's subtree at depth d (the root is depth 0); 0 when there are none
    def countAtDepthInSubtree(self, node, d):
        if not self.lo <= node <= self.hi:
            self._bad("countAtDepthInSubtree", node)
        if d < 0 or d + 1 >= len(self.depthStart):
            return 0
        s, e = self.depthStart[d], self.depthStart[d + 1]
        l = self.pos[node]
        return bisect_left(self.depthPos, l + self.sz[node], s, e) - bisect_left(self.depthPos, l, s, e)

    # O(log n) -- lca of a and b if the tree were rooted at r instead
    def lcaRootedAt(self, r, a, b):
        if not (self.lo <= r <= self.hi and self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lcaRootedAt", r, a, b)
        return self._median(a, b, r)

    # O(log n) -- node's parent if the tree were rooted at r (-1 when node == r)
    def parentRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("parentRootedAt", r, node)
        return -1 if node == r else self._next(node, r)

    # O(log n) -- size of node's subtree if the tree were rooted at r
    def subtreeSizeRootedAt(self, r, node):
        if not (self.lo <= r <= self.hi and self.lo <= node <= self.hi):
            self._bad("subtreeSizeRootedAt", r, node)
        if node == r:
            return self.n
        if self._isAncestor(node, r):  # r hangs below node: everything but the child holding r
            return self.n - self.sz[self._kth(r, self.dep[r] - self.dep[node] - 1)]
        return self.sz[node]

    # O(log n) -- the kth node walking a -> b (k = 0 is a, k = unweightedDist(a, b) is b; -1 if k is past b); needs
    # k >= 0
    def kthNodeOnPath(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("kthNodeOnPath", a, b)
        if k < 0:
            raise IndexError(f"kthNodeOnPath: needs k >= 0, got {k}")
        dep = self.dep
        c = self._lca(a, b)
        up = dep[a] - dep[c]
        total = up + dep[b] - dep[c]
        if k > total:
            return -1
        return self._kth(a, k) if k <= up else self._kth(b, total - k)

    # O(log n) -- the neighbor of a one step toward b (-1 if a == b)
    def nextNodeOnPath(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nextNodeOnPath", a, b)
        return -1 if a == b else self._next(a, b)

    # O(log n) -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # O(log n) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # O(log n) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # O(log n) -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # O(log n) -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # O(K + log n) -- every node on the path a..b, in order from a (K = how many)
    def pathNodes(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("pathNodes", a, b)
        par = self.par
        c = self._lca(a, b)
        out = []
        while a != c:
            out.append(a)
            a = par[a]
        out.append(c)
        tail = []
        while b != c:
            tail.append(b)
            b = par[b]
        tail.reverse()
        return out + tail
