# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-hash-fenwick-node/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathHash nodePathHashReversed nodePathIsPalindrome nodePathsEqual nodeSubtreeAdd parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
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
#   nodeChmax: log(N)
#   nodeChmin: log(N)
#   nodeGet: log(N)
#   nodePathHash: log(N)
#   nodePathHashReversed: log(N)
#   nodePathIsPalindrome: log(N)
#   nodePathsEqual: log(N)
#   nodeSubtreeAdd: log(N)
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
#   node: up[1*N] low[1*N] added[1*N]
#   tags: none
#   other: val[1*N] pw[1*N] ipw[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: three Fenwick trees over the positions; pw / ipw are as long as the tree is deep

import random
from bisect import bisect_left

_HP = (1 << 61) - 1  # hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


# tree = Tree(edges, root, vals)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30])       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30])    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each subtree is one stretch of positions
# (pos[node] .. pos[node] + sz[node] - 1). Two sums are kept along the path from the root to every node v: the sum of
# hash(node) * base^depth, and the sum of hash(node) / base^depth. The difference of two of the first is the hash of the
# stretch between, read upwards, times base^(the depth of its top), which an inverse power takes off; the second times
# base^depth(v) is the hash of root..v read downwards. A path a -> b is the way up to the lca and the way down from it,
# joined like any two hashes. Each term sits at its node's position in a Fenwick tree and is taken back just past that
# node's subtree, so a prefix up to pos[v] is the sum along root..v, and one value changing is two point writes: one log
# for everything, where chain pieces would take two. A subtree add makes each sum grow by a geometric sum of powers of
# the base: the part that is the same all over the subtree goes into the trees like a value, and the rest is (the total
# added to that node, a third Fenwick tree) times a power that depends on the node's depth only. No path updates, and no
# assign over a subtree.
class Tree:
    # O(n) -- builds the layout and the Fenwick trees; raises ValueError when the edges are not one tree on nodes 0..n-1
    # or 1..n, or vals has the wrong length
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
        val = list(vals)  # what each node was given, before any subtree add

        deepest = dep[bfs[-1]]
        pw, ipw = [1] * (deepest + 2), [1] * (deepest + 2)
        inverse = pow(_HB, _HP - 2, _HP)
        for d in range(1, deepest + 2):
            pw[d] = pw[d - 1] * _HB % _HP
            ipw[d] = ipw[d - 1] * inverse % _HP
        # Three Fenwick trees over positions 1..n, each read by prefixes (a term goes in at its node's position and is
        # taken back just past that node's subtree, so the prefix up to pos[v] sums over the path root..v). up:
        # hash(node) * base^depth. low: hash(node) / base^depth. added: what subtree adds gave, so its prefix up to
        # pos[v] is the total added to v. pw[d] = base^d and ipw[d] = 1 / base^d.
        up, low = [0] * (n + 2), [0] * (n + 2)
        for v in bfs:
            h = (val[v] + _HO) % _HP
            i = pos[v] + 1
            j = i + sz[v]
            x = h * pw[dep[v]] % _HP
            up[i] += x
            up[j] -= x
            x = h * ipw[dep[v]] % _HP
            low[i] += x
            low[j] -= x
        for i in range(1, n + 1):
            up[i] %= _HP
            low[i] %= _HP
            j = i + (i & -i)
            if j <= n:
                up[j] += up[i]
                low[j] += low[i]
        self.val, self.up, self.low, self.added, self.pw, self.ipw = val, up, low, [0] * (n + 2), pw, ipw
        # 1 / (B - 1) and B / (B - 1): what a geometric sum of powers of the base is divided by (see SubtreeAdd)
        self.geo = pow(_HB - 1, _HP - 2, _HP)
        self.geoB = self.geo * _HB % _HP

    # add x at every position i..j-1 of a tree read by prefixes: x goes in at i and is taken back at j
    def _spread(self, tree, i, j, x, mod):
        n = self.n
        while i <= n:
            tree[i] += x
            if mod:
                tree[i] %= mod
            i += i & -i
        while j <= n:
            tree[j] -= x
            if mod:
                tree[j] %= mod
            j += j & -j

    # the sum of positions 1..i of a tree
    def _upTo(self, tree, i):
        res = 0
        while i > 0:
            res += tree[i]
            i -= i & -i
        return res

    # the value kept at node v right now (what it was given, plus every subtree add that reached it)
    def _value(self, v):
        return self.val[v] + self._upTo(self.added, self.pos[v] + 1)

    # the value kept at node v changes by d
    def _change(self, v, d):
        i = self.pos[v] + 1
        j = i + self.sz[v]
        k = self.dep[v]
        self.val[v] += d
        d %= _HP
        self._spread(self.up, i, j, d * self.pw[k] % _HP, _HP)
        self._spread(self.low, i, j, d * self.ipw[k] % _HP, _HP)

    # the sum of hash(value) * base^depth over the node values on the path root..v
    def _upSum(self, v):
        i = self.pos[v] + 1
        return (self._upTo(self.up, i) + self._upTo(self.added, i) % _HP * self.geoB % _HP * self.pw[self.dep[v]]) % _HP

    # the hash of the node values on the path root..v, read downwards
    def _downHash(self, v):
        i = self.pos[v] + 1
        k = self.dep[v]
        low = (self._upTo(self.low, i) - self._upTo(self.added, i) % _HP * self.geo % _HP * self.ipw[k]) % _HP
        return low * self.pw[k] % _HP

    # the hash of the node values read walking a -> b
    def _hash(self, a, b):
        dep = self.dep
        c = self._lca(a, b)
        d = dep[c]
        # the way up: a .. lca, the lca being its top
        above = self._upSum(self.par[c]) if c != self.root else 0
        head = (self._upSum(a) - above) * self.ipw[d] % _HP
        m = dep[b] - d  # how many values the way down from the lca holds
        return ((head - self._downHash(c)) * self.pw[m] + self._downHash(b)) % _HP

    # O(log n) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        v = node
        return self._value(v)

    # O(log n) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        v = node
        self._change(v, x - self._value(v))

    # O(log n) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        v = node
        self._change(v, x)

    # O(log n) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        v = node
        now = self._value(v)
        if x > now:
            self._change(v, x - now)

    # O(log n) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        v = node
        now = self._value(v)
        if x < now:
            self._change(v, x - now)

    # O(log n) -- val += x for every node in node's subtree
    def nodeSubtreeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAdd", node)
        i = self.pos[node] + 1
        j = self.pos[node] + 1 + self.sz[node]
        top = self.dep[node]  # the depth of the shallowest value changed
        self._spread(self.added, i, j, x, 0)
        m = x % _HP
        # each sum grows by a geometric sum of powers; here, the part that is the same all over the subtree
        self._spread(self.up, i, j, -m * self.geo % _HP * self.pw[top] % _HP, _HP)
        self._spread(self.low, i, j, m * self.geoB % _HP * self.ipw[top] % _HP, _HP)

    # O(log n) -- hash of the node values read a -> b (mod 2^61 - 1, random base): equal sequences hash equal
    def nodePathHash(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathHash", a, b)
        return self._hash(a, b)

    # O(log n) -- hash of the node values read b -> a (equal to nodePathHash(b, a))
    def nodePathHashReversed(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathHashReversed", a, b)
        return self._hash(b, a)

    # O(log n) -- do the node values read the same a -> b and b -> a?
    def nodePathIsPalindrome(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathIsPalindrome", a, b)
        return self._hash(a, b) == self._hash(b, a)

    # O(log n) -- do the node values read a -> b equal those read c -> d?
    def nodePathsEqual(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("nodePathsEqual", a, b, c, d)
        return self._dist(a, b) == self._dist(c, d) and self._hash(a, b) == self._hash(c, d)

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
