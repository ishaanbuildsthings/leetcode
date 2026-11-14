# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-xor-apply-fenwick-edge/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathXORApply edgeSubtreeXOR edgeSubtreeXORApply isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: euler-fenwick
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)
#   edgeAssign: log(N)
#   edgeChmax: log(N)
#   edgeChmin: log(N)
#   edgeGet: log(N)
#   edgePathXORApply: log(N)
#   edgeSubtreeXOR: log(N)
#   edgeSubtreeXORApply: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
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
#   layout: none
#   node: marks[2*N] diffs[2*N]
#   tags: none
#   other: base[1*N] first[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]

from bisect import bisect_left


# tree = Tree(edges, root)
#
# edges: the tree's n - 1 edges with their weights. Whether nodes are 0..n-1 or 1..n is detected automatically from
#        the edge list (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b, w), ...]     e.g. [(0, 1, 5), (1, 2, 7)]
# root: the root node (required), e.g. 0 or 1.
#
#   Tree([(0, 1, 5), (1, 2, 7)], 0)    # nodes 0..2, rooted at 0
#   Tree([(1, 2, 5), (2, 3, 7)], 1)    # nodes 1..3, rooted at 1
#
# An edge is named by its two ends in either order: (a, b) and (b, a) are the same edge. A path a..b covers the edges
# between a and b, and a subtree covers the edges below node. A search that finds an edge returns its lower end (the end
# farther from the root). A query with no edges to look at (a path a..a, a leaf's subtree) says what it returns. Nodes
# go in and come out with your labels, -1 means "none", and a label that is not in the tree raises IndexError. Nothing
# recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions
# (pos[node] .. pos[node] + sz[node] - 1). A path xor is not spread over the path: it leaves marks, x at both ends of
# the path (an edge is kept at its lower end, so the lca's own position must not gain anything: with xor the two ends'
# marks already cancel there). The value of an edge is then its starting value xored with every mark inside its subtree:
# an edge on the path has exactly one end below it, and one off the path has no mark below it or a set that cancels.
# "Every mark inside a subtree" is one Fenwick range xor, so a path update is O(log n), where a wrapped range template
# needs O(log^2 n). For a subtree's xor a mark at y counts once per edge between y and the subtree's top, so only the
# marks at the right depth parity are seen: the marks are kept in two trees, by even and odd depth. Subtree updates are
# kept apart as "xor over a stretch of positions" (two more trees, by even and odd position). One value changes through
# a mark at it, taken back at its parent. There is no single-log path xor here: a path update together with a path query
# needs the O(log^2 n) templates.
class Tree:
    # O(n) -- builds the layout and the sums of the starting values; raises ValueError when the edges are not one tree
    # on nodes 0..n-1 or 1..n, or an edge has no weight
    def __init__(self, edges, root):
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
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        base = [0] * (hi + 1)
        for e in edges:
            base[e[0] if par[e[0]] == e[1] else e[1]] = e[2]

        # base[v]: the weight of the edge above v at the start (the root has none) (it never changes: every update is
        # kept in the trees). first[i]: the starting values at positions below i, xored together.
        first = [0] * (n + 1)
        for i, v in enumerate(order):
            first[i + 1] = first[i] ^ base[v]
        self.base, self.first = base, first
        # Fenwick trees over the positions (1-based), kept with xor. marks[0], marks[1]: the marks at nodes of even and
        # of odd depth. diffs[0], diffs[1]: where a stretch xor starts and stops, at even and at odd positions.
        self.marks = ([0] * (n + 1), [0] * (n + 1))
        self.diffs = ([0] * (n + 1), [0] * (n + 1))

    # tree[p] ^= x, tree a Fenwick tree over the positions (nothing when p is past the last position)
    def _flip(self, tree, p, x):
        n = self.n
        p += 1
        while p <= n:
            tree[p] ^= x
            p += p & -p

    # the xor of tree's entries at positions 0..k (0 when k is -1)
    def _xor(self, tree, k):
        res = 0
        k += 1
        while k > 0:
            res ^= tree[k]
            k -= k & -k
        return res

    # a mark of x at node v: every edge from v up to the root has x once more inside its subtree
    def _mark(self, v, x):
        self._flip(self.marks[self.dep[v] & 1], self.pos[v], x)

    # the value kept at node v is xored with x (it alone): a mark at v, taken back at its parent
    def _bump(self, v, x):
        self._mark(v, x)
        if v != self.root:
            self._mark(self.par[v], x)

    # every value at positions l..r is xored with x (nothing for an empty stretch, l > r)
    def _spread(self, l, r, x):
        if l > r:
            return
        self._flip(self.diffs[l & 1], l, x)
        self._flip(self.diffs[(r + 1) & 1], r + 1, x)

    # the value kept at node v: its starting value, the marks inside its subtree, the stretch xors that cover it
    def _value(self, v):
        l = self.pos[v]
        r = l + self.sz[v] - 1
        xor, (m0, m1), (d0, d1) = self._xor, self.marks, self.diffs
        return self.base[v] ^ xor(m0, r) ^ xor(m0, l - 1) ^ xor(m1, r) ^ xor(m1, l - 1) ^ xor(d0, l) ^ xor(d1, l)

    # what the stretch xors gave the values at positions 0..k, xored together (0 when k is -1): a stretch that starts
    # at j covers an odd number of them when j and k are both even or both odd
    def _spreadUpTo(self, k):
        return self._xor(self.diffs[k & 1], k)

    # the lower end of the edge a - b, the node its weight is kept under (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return a
        if self.par[b] == a:
            return b
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(log n) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        v = self._edge("edgeGet", a, b)
        return self._value(v)

    # O(log n) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        v = self._edge("edgeAssign", a, b)
        self._bump(v, w ^ self._value(v))

    # O(log n) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        v = self._edge("edgeAdd", a, b)
        now = self._value(v)
        self._bump(v, (now + w) ^ now)

    # O(log n) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        v = self._edge("edgeChmax", a, b)
        now = self._value(v)
        if w > now:
            self._bump(v, w ^ now)

    # O(log n) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        v = self._edge("edgeChmin", a, b)
        now = self._value(v)
        if w < now:
            self._bump(v, w ^ now)

    # O(log n) -- weight ^= w for every edge on the path a..b (nothing when a == b)
    def edgePathXORApply(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathXORApply", a, b)
        # (an edge is kept at its lower end: the lca's own marks would cancel)
        self._mark(a, w)
        self._mark(b, w)

    # O(log n) -- weight ^= w for every edge in node's subtree
    def edgeSubtreeXORApply(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeXORApply", node)
        l = self.pos[node]
        self._spread(l + 1, l + self.sz[node] - 1, w)

    # O(log n) -- XOR of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeXOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeXOR", node)
        l = self.pos[node]
        r = l + self.sz[node] - 1
        # a mark at y is seen once for every edge between y and node: an odd number of times when y's depth is the other
        # kind (even / odd) than node's
        m = self.marks[(self.dep[node] + 1) & 1]
        return (self.first[r + 1] ^ self.first[l + 1] ^ self._xor(m, r) ^ self._xor(m, l - 1)
                ^ self._spreadUpTo(r) ^ self._spreadUpTo(l))

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
