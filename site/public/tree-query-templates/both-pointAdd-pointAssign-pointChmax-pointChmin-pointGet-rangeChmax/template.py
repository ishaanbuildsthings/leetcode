# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmax/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmax/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathChmax edgeSubtreeChmax isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathChmax nodeSubtreeChmax parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)
#   edgeAssign: log(N)
#   edgeChmax: 1
#   edgeChmin: log(N)
#   edgeGet: log(N)
#   edgePathChmax: log^2(N)
#   edgeSubtreeChmax: log(N)
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
#   nodeChmax: 1
#   nodeChmin: log(N)
#   nodeGet: log(N)
#   nodePathChmax: log^2(N)
#   nodeSubtreeChmax: log(N)
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
#   node: tree[2*N]
#   tags: tree[2*N]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeChmax tag (no aggregates); leaves count as node data, internal nodes as tags

# rangeChmax + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
# rangeChmax composes with itself in any order, so a range update only tags the O(logN) covering nodes and pointGet
# folds the tags on the leaf-to-root path. Only pointAssign-style overwrites need to push those tags off the path first,
# because they must not be re-applied to the new value.
class RangeChmaxTree:
    __slots__ = ("n", "tree")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.tree = [float("-inf")] * n + list(arr)

    # O(logN) -- a[i] = max(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeChmax(self, l, r, v):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeChmax: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        tree = self.tree
        l += self.n
        r += self.n + 1
        while l < r:
            if l & 1:
                tree[l] = tree[l] if tree[l] > v else v
                l += 1
            if r & 1:
                r -= 1
                tree[r] = tree[r] if tree[r] > v else v
            l >>= 1
            r >>= 1

    # O(logN) -- move the tags on i's root-to-leaf path down, so nothing above i is pending
    def _push(self, p):
        tree = self.tree
        for h in range(p.bit_length() - 1, 0, -1):
            x = p >> h
            t = tree[x]
            if t != float("-inf"):
                y = x << 1
                tree[y] = tree[y] if tree[y] > t else t
                tree[y | 1] = tree[y | 1] if tree[y | 1] > t else t
                tree[x] = float("-inf")

    # O(logN) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        tree = self.tree
        p = i + self.n
        a = tree[p]
        p >>= 1
        while p:
            t = tree[p]
            a = a if a > t else t
            p >>= 1
        return a

    # O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    # each node's tag is complete when it is pushed), then read the leaves
    def getAll(self):
        tree = self.tree
        for x in range(1, self.n):
            t = tree[x]
            if t != float("-inf"):
                y = x << 1
                tree[y] = tree[y] if tree[y] > t else t
                tree[y | 1] = tree[y | 1] if tree[y | 1] > t else t
                tree[x] = float("-inf")
        return self.tree[self.n:]

    # O(logN) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.tree[p] = val

    # O(logN) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        self.tree[p] = (self.tree[p] + delta)

    # O(1) -- a[i] = max(a[i], val); a leaf-level chmax tag commutes with the pending ones above it; needs 0 <= i < n,
    # else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        if val > self.tree[p]:
            self.tree[p] = val

    # O(logN) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        if val < self.tree[p]:
            self.tree[p] = val


from bisect import bisect_left


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# The node... ops act on the node values and the edge... ops on the edge weights: the two never affect each other. For
# nodes, a path a..b includes both a and b. For edges, a path a..b covers the edges between a and b and a subtree the
# edges below node; an edge is named by its two ends in either order, a search that finds an edge returns its lower end
# (the end farther from the root), and a query with no edges to look at (a path a..a, a leaf's subtree) says what it
# returns. Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises
# IndexError. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (RangeChmaxTree)
# sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower
# end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain
# it crosses.
class Tree:
    # O(n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
    def __init__(self, edges, root, vals):
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
        self.nodeSeg = RangeChmaxTree([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = RangeChmaxTree(arr)  # each edge's weight, at its lower end's position

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

    # O(1) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.nodeSeg.pointChmax(self.pos[node], x)

    # O(log n) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.nodeSeg.pointChmin(self.pos[node], x)

    # O(log^2 n) -- val = max(val, x) for every node on the path a..b
    def nodePathChmax(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathChmax", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeChmax
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, x) if l <= r else apply(r, l, x)

    # O(log n) -- val = max(val, x) for every node in node's subtree
    def nodeSubtreeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeChmax", node)
        l = self.pos[node]
        self.nodeSeg.rangeChmax(l, l + self.sz[node] - 1, x)

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

    # O(1) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        self.edgeSeg.pointChmax(self._edge("edgeChmax", a, b), w)

    # O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        self.edgeSeg.pointChmin(self._edge("edgeChmin", a, b), w)

    # O(log^2 n) -- weight = max(weight, w) for every edge on the path a..b
    def edgePathChmax(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathChmax", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeChmax
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], w)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, w) if l < r else apply(r + 1, l, w)

    # O(log n) -- weight = max(weight, w) for every edge in node's subtree
    def edgeSubtreeChmax(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeChmax", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.edgeSeg.rangeChmax(l, r, w)

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
