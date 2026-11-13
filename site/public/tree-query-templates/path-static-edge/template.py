# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-static-edge/template.py
# @operations: countAtDepthInSubtree depth edgeGet edgePathHash edgePathHashReversed edgePathIsPalindrome edgePathSum edgePathXOR edgePathsEqual edgeSubtreeSum edgeSubtreeXOR isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: root-prefix
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeGet: 1
#   edgePathHash: 1
#   edgePathHashReversed: 1
#   edgePathIsPalindrome: 1
#   edgePathSum: 1
#   edgePathXOR: 1
#   edgePathsEqual: 1
#   edgeSubtreeSum: 1
#   edgeSubtreeXOR: 1
#   isAncestor: 1
#   isOnPath: 1
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: 1
#   lcaRootedAt: 1
#   median: 1
#   nextNodeOnPath: log(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: 1
#   pathNodes: K
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: 1
#   unweightedDistBetweenPaths: 1
#   unweightedDistToPath: 1
#   build: N*log(N)
# @memory:
#   layout: none
#   node: sumTo[1*N] xorTo[1*N] sumAt[1*N] xorAt[1*N] down[1*N] up[1*N]
#   tags: none
#   other: val[1*N] pw[1*N] ipw[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N] table[1*N*log(N)]
#   note: the n log n part is the lca table (what makes every query O(1)); pw / ipw are as long as the tree is deep

import random
from bisect import bisect_left

_HP = (1 << 61) - 1  # hashes are mod this prime
_HB = random.randrange(1 << 40, _HP - 1)  # with a base picked at random each run (so no test can be built against it)
_HO = random.randrange(1, _HP)  # value v hashes as v + _HO: no common value hashes as 0 (a 0 in front would vanish)


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
# How it works: the values never change, so a sum, a xor and a hash along the path from the root to a node are kept for
# every node, and a path a..b is two or three reads of them around the lca of a and b. The lca is O(1): one heavy-light
# pass gives every node a position, and a sparse table over the positions finds it (between two nodes' positions, the
# parent that sits earliest is their lca). A subtree is one stretch of positions (pos[node] .. pos[node] + sz[node] -
# 1), so prefix arrays over the positions give its sum and xor. For the hash, up[v] is the sum of hash(edge) *
# base^depth along root..v: the difference of two of them is the hash of the stretch between, read upwards, times
# base^(the depth of its top), which an inverse power of the base takes off. down[v] is the hash of root..v read
# downwards. The way up to the lca and the way down from it are then joined like any two hashes.
class Tree:
    # O(n log n) -- builds the layout, the lca table and the sums from the root; raises ValueError when the edges are
    # not one tree on nodes 0..n-1 or 1..n, or an edge has no weight
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

        # table[j][i] = the earliest parent position among the nodes at positions i .. i + 2^j - 1
        row = [0] * n
        for i in range(1, n):
            row[i] = pos[par[order[i]]]
        table = [row]
        half = 1
        while 2 * half < n:
            row = [row[i] if row[i] < row[i + half] else row[i + half] for i in range(n - 2 * half + 1)]
            table.append(row)
            half *= 2
        self.table = table

        self.n, self.lo, self.hi, self.root = n, lo, hi, root
        self.par, self.dep, self.sz, self.head, self.pos, self.order = par, dep, sz, head, pos, order
        self.depthStart, self.depthPos = depthStart, depthPos
        for e in edges:
            if len(e) != 3:
                raise ValueError(f"Tree: every edge needs its weight here, (a, b, w), got {e}")
        val = [0] * (hi + 1)  # val[v]: the weight of the edge above v (the root has none)
        for e in edges:
            val[e[0] if par[e[0]] == e[1] else e[1]] = e[2]

        # val[v]: the weight of the edge above v (the root has none). Along the path root..v: sumTo[v] and xorTo[v] (the
        # sum and the xor of its edge weights), down[v] (their hash read downwards) and up[v] (the sum of hash(value) *
        # base^depth). Over the positions: sumAt[i] and xorAt[i], the sum and the xor of the values at positions below
        # i. pw[d] = base^d and ipw[d] = 1 / base^d.
        deepest = max(dep[v] for v in order)
        pw, ipw = [1] * (deepest + 2), [1] * (deepest + 2)
        inverse = pow(_HB, _HP - 2, _HP)
        for d in range(1, deepest + 2):
            pw[d] = pw[d - 1] * _HB % _HP
            ipw[d] = ipw[d - 1] * inverse % _HP
        sumTo, xorTo, down, up = [0] * (hi + 1), [0] * (hi + 1), [0] * (hi + 1), [0] * (hi + 1)
        sumAt, xorAt = [0] * (n + 1), [0] * (n + 1)
        for i, v in enumerate(order):
            x = val[v]
            sumAt[i + 1] = sumAt[i] + x
            xorAt[i + 1] = xorAt[i] ^ x
            if v == root:
                continue  # (no edge above the root: its sums stay 0)
            p = par[v]
            h = (x + _HO) % _HP
            sumTo[v] = sumTo[p] + x
            xorTo[v] = xorTo[p] ^ x
            down[v] = (down[p] * _HB + h) % _HP
            up[v] = (up[p] + h * pw[dep[v]]) % _HP
        self.val, self.sumTo, self.xorTo, self.sumAt, self.xorAt = val, sumTo, xorTo, sumAt, xorAt
        self.down, self.up, self.pw, self.ipw = down, up, pw, ipw

    # the hash of the edge weights read walking a -> b
    def _hash(self, a, b):
        dep, down = self.dep, self.down
        c = self._lca(a, b)
        d = dep[c]
        # the way up: the edges below the lca, the shallowest one level under it
        head = (self.up[a] - self.up[c]) * self.ipw[d + 1] % _HP
        m = dep[b] - d  # how many values the way down from the lca holds
        return ((head - down[c]) * self.pw[m] + down[b]) % _HP

    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgeGet", a, b)
        if self.par[a] == b:
            return self.val[a]
        if self.par[b] == a:
            return self.val[b]
        raise IndexError(f"edgeGet: needs an edge between a and b, got {a} and {b}")

    # O(1) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSum", a, b)
        sumTo = self.sumTo
        return sumTo[a] + sumTo[b] - 2 * sumTo[self._lca(a, b)]

    # O(1) -- xor of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathXOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathXOR", a, b)
        return self.xorTo[a] ^ self.xorTo[b]

    # O(1) -- hash of the edge weights read a -> b (mod 2^61 - 1, random base): equal sequences hash equal; 0 when a ==
    # b (no edges)
    def edgePathHash(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathHash", a, b)
        return self._hash(a, b)

    # O(1) -- hash of the edge weights read b -> a (equal to edgePathHash(b, a)); 0 when a == b (no edges)
    def edgePathHashReversed(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathHashReversed", a, b)
        return self._hash(b, a)

    # O(1) -- do the edge weights read the same a -> b and b -> a? (True when a == b: no edges)
    def edgePathIsPalindrome(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathIsPalindrome", a, b)
        return self._hash(a, b) == self._hash(b, a)

    # O(1) -- do the edge weights read a -> b equal those read c -> d? (two paths with no edges are equal)
    def edgePathsEqual(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("edgePathsEqual", a, b, c, d)
        return self._dist(a, b) == self._dist(c, d) and self._hash(a, b) == self._hash(c, d)

    # O(1) -- sum of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeSum", node)
        l = self.pos[node]
        return self.sumAt[l + self.sz[node]] - self.sumAt[l + 1]

    # O(1) -- xor of the edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeXOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeXOR", node)
        l = self.pos[node]
        return self.xorAt[l + self.sz[node]] ^ self.xorAt[l + 1]

    def _bad(self, name, *nodes):
        raise IndexError(f"{name}: needs {self.lo} <= node <= {self.hi}, got {', '.join(map(str, nodes))}")

    def _lca(self, a, b):
        if a == b:
            return a
        l, r = self.pos[a], self.pos[b]
        if l > r:
            l, r = r, l
        j = (r - l).bit_length() - 1
        row = self.table[j]
        x, y = row[l + 1], row[r - (1 << j) + 1]
        return self.order[x if x < y else y]

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

    # O(1) -- lowest common ancestor of a and b
    def lca(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("lca", a, b)
        return self._lca(a, b)

    # O(1) -- number of edges on the path a..b
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

    # O(1) -- lca of a and b if the tree were rooted at r instead
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

    # O(1) -- does the path a..b pass through node? (a and b count)
    def isOnPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("isOnPath", a, b, node)
        return self._onPath(a, b, node)

    # O(1) -- fewest edges from node to any node on the path a..b (0 if node is on it)
    def unweightedDistToPath(self, a, b, node):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= node <= self.hi):
            self._bad("unweightedDistToPath", a, b, node)
        return self._dist(node, self._median(a, b, node))

    # O(1) -- fewest edges between any node on path a..b and any node on path c..d (0 if they share a node)
    def unweightedDistBetweenPaths(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("unweightedDistBetweenPaths", a, b, c, d)
        p = self._median(a, b, c)  # where c's side meets the path a..b
        if p != self._median(a, b, d):
            return 0  # c and d meet it at different nodes, so c..d runs along it
        return self._dist(p, self._median(c, d, p))

    # O(1) -- the one node that lies on all three paths between a, b and c
    def median(self, a, b, c):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi and self.lo <= c <= self.hi):
            self._bad("median", a, b, c)
        return self._median(a, b, c)

    # O(1) -- the shared part of paths a..b and c..d as its two end nodes (p, q), p first walking a -> b; p == q
    # if they share one node; (-1, -1) if they share none
    def pathIntersection(self, a, b, c, d):
        lo, hi = self.lo, self.hi
        if not (lo <= a <= hi and lo <= b <= hi and lo <= c <= hi and lo <= d <= hi):
            self._bad("pathIntersection", a, b, c, d)
        p, q = self._median(a, b, c), self._median(a, b, d)  # where c's side and d's side meet the path a..b
        if p == q:
            return (p, p) if self._onPath(c, d, p) else (-1, -1)
        return (p, q) if self._dist(a, p) < self._dist(a, q) else (q, p)

    # O(K) -- every node on the path a..b, in order from a (K = how many)
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
