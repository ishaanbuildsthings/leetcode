# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/subtree-depth-add-mod-fenwick-node/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeGet nodePathSumMod nodeSubtreeAddByDepthMod nodeSubtreeAddMod nodeSubtreeSumMod parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: euler-fenwick
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
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
#   nodePathSumMod: log(N)
#   nodeSubtreeAddByDepthMod: log(N)
#   nodeSubtreeAddMod: log(N)
#   nodeSubtreeSumMod: log(N)
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
#   node: ca[1*N] cb[1*N] sa[1*N] sb[1*N] up[1*N]
#   tags: none
#   other: base[1*N] first[1*N] depSum[1*N] rootSum[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]

from bisect import bisect_left


# tree = Tree(edges, root, vals, mod)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
# mod: the modulus MOD (every value is kept in [0, MOD)).
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30], mod)       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30], mod)    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions
# (pos[node] .. pos[node] + sz[node] - 1). Adding by depth gives the node at depth d the amount A + B * d, with the same
# A and B for the whole subtree (B = step, and A = start minus step times the depth where the subtree starts). So every
# update is "add A + B * depth over a stretch of positions", and five Fenwick trees over the positions keep them. ca and
# cb are difference trees: a prefix sum is the A (the B) that applies at a position, which gives one value. sa and sb
# are their partners for a sum over a stretch (sb weighs each B by the depths it covers), which gives a subtree's sum.
# up keeps what the updates added to the path from the root down to a node, apart from the part that follows from that
# node's own depth d: A * d + B * (0 + 1 + ... + d). With it the sum on root..v is one read, and a path a..b is root..a
# plus root..b minus what lies above their lca.
class Tree:
    # O(n) -- builds the layout and the sums of the starting values; raises ValueError when the edges are not one tree
    # on nodes 0..n-1 or 1..n, or vals has the wrong length
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
        base = [x % mod for x in vals]

        # base[v]: v's value at the start, plus what was added to it alone. first[i]: the starting values at positions
        # below i, summed. depSum[i]: the depths at positions below i, summed. rootSum[v]: the starting values on the
        # path root..v, summed.
        first, depSum, rootSum = [0] * (n + 1), [0] * (n + 1), [0] * (hi + 1)
        for i, v in enumerate(order):
            first[i + 1] = (first[i] + base[v]) % mod
            depSum[i + 1] = (depSum[i] + dep[v]) % mod
            rootSum[v] = (base[v] + (rootSum[par[v]] if v != root else 0)) % mod
        self.base, self.first, self.depSum, self.rootSum = base, first, depSum, rootSum

        # Five Fenwick trees over the positions (1-based), filled by the updates, each "add A + B * depth over a
        # stretch": ca, cb (a prefix sum is the A, the B that applies at a position), sa, sb (with them, the sum over a
        # stretch) and up (what the updates gave the path from the root, apart from its depth terms).
        self.ca, self.cb, self.sa, self.sb, self.up = ([0] * (n + 1) for _ in range(5))
        self.mod = mod

    # one Fenwick step in all five trees: from position p on, ca += a, cb += b, sa += c, sb += d, up += e (nothing when
    # p is past the last position)
    def _mark(self, p, a, b, c, d, e):
        ca, cb, sa, sb, up, n = self.ca, self.cb, self.sa, self.sb, self.up, self.n
        mod = self.mod
        p += 1
        while p <= n:
            ca[p] = (ca[p] + a) % mod
            cb[p] = (cb[p] + b) % mod
            sa[p] = (sa[p] + c) % mod
            sb[p] = (sb[p] + d) % mod
            up[p] = (up[p] + e) % mod
            p += p & -p

    # the five trees' prefix sums through position p: (ca, cb, sa, sb, up)
    def _read(self, p):
        ca, cb, sa, sb, up = self.ca, self.cb, self.sa, self.sb, self.up
        a = b = c = d = e = 0
        p += 1
        while p > 0:
            a += ca[p]
            b += cb[p]
            c += sa[p]
            d += sb[p]
            e += up[p]
            p -= p & -p
        return a, b, c, d, e

    # every value at positions l..r gets A + B * (its depth) added; top: the depth of the shallowest of them (nothing
    # for an empty stretch, l > r)
    def _spread(self, l, r, top, A, B):
        if l > r:
            return
        depSum = self.depSum
        # what a path from the root gains, apart from its depth terms
        C = A * (1 - top) - B * (top * (top - 1) // 2)
        self._mark(l, A, B, A * l, B * depSum[l], C)
        self._mark(r + 1, -A, -B, -A * (r + 1), -B * depSum[r + 1], -C)

    # the value kept at node v grows by x (it alone)
    def _bump(self, v, x):
        self.base[v] = (self.base[v] + x) % self.mod
        p = self.pos[v]
        self._mark(p, 0, 0, -x, 0, x)
        self._mark(p + self.sz[v], 0, 0, 0, 0, -x)

    # the value kept at node v
    def _value(self, v):
        a, b, _, _, _ = self._read(self.pos[v])
        return (self.base[v] + a + b * self.dep[v]) % self.mod

    # the sum of the values at positions 0..k (0 when k is -1)
    def _upTo(self, k):
        a, b, c, d, _ = self._read(k)
        return (self.first[k + 1] + (k + 1) * a - c + self.depSum[k + 1] * b - d) % self.mod

    # the sum of the values kept on the path root..v
    def _fromRoot(self, v):
        a, b, _, _, e = self._read(self.pos[v])
        d = self.dep[v]
        return (self.rootSum[v] + e + a * d + b * (d * (d + 1) // 2)) % self.mod

    # O(log n) -- val(node) (kept in [0, MOD))
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self._value(node)

    # O(log n) -- val(node) = x % MOD
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self._bump(node, x - self._value(node))

    # O(log n) -- val(node) = (val + x) % MOD
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self._bump(node, x)

    # O(log n) -- val = (val + x) % MOD for every node in node's subtree
    def nodeSubtreeAddMod(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAddMod", node)
        l = self.pos[node]
        self._spread(l, l + self.sz[node] - 1, self.dep[node], x, 0)

    # O(log n) -- every node u in node's subtree gets start + step * (depth(u) - depth(node)) added, all mod MOD
    def nodeSubtreeAddByDepthMod(self, node, start, step):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAddByDepthMod", node)
        l = self.pos[node]
        top = self.dep[node]
        self._spread(l, l + self.sz[node] - 1, top, start - step * top, step)

    # O(log n) -- sum of the node values in node's subtree, mod MOD
    def nodeSubtreeSumMod(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSumMod", node)
        l = self.pos[node]
        return (self._upTo(l + self.sz[node] - 1) - self._upTo(l - 1)) % self.mod

    # O(log n) -- sum of the node values on the path a..b, mod MOD
    def nodePathSumMod(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumMod", a, b)
        c = self._lca(a, b)
        res = self._fromRoot(a) + self._fromRoot(b) - self._fromRoot(c)
        if c != self.root:
            res -= self._fromRoot(self.par[c])
        return res % self.mod

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
