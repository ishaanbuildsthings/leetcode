# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-distinct-bitset-edge/template.py
# @operations: countAtDepthInSubtree depth edgeAdd edgeAssign edgeChmax edgeChmin edgeGet edgePathAllDistinct edgePathAssign edgePathCountDistinct edgeSubtreeAllDistinct edgeSubtreeAssign edgeSubtreeCountDistinct isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: bitset-seg-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAdd: log(N)*D/64 amortized
#   edgeAssign: log(N)*D/64 amortized
#   edgeChmax: log(N)*D/64 amortized
#   edgeChmin: log(N)*D/64 amortized
#   edgeGet: log(N)
#   edgePathAllDistinct: log^2(N)*D/64
#   edgePathAssign: log^2(N)*D/64 amortized
#   edgePathCountDistinct: log^2(N)*D/64
#   edgeSubtreeAllDistinct: log(N)*D/64
#   edgeSubtreeAssign: log(N)*D/64 amortized
#   edgeSubtreeCountDistinct: log(N)*D/64
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
#   build: N*D/64
# @memory:
#   layout: none
#   node: bits[2*N*D/64]
#   tags: tag[2*N]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: D = how many distinct values ever appeared (a value keeps its bit once it has one); a bitset is D / 64 words. C++ widens every bitset by half when a new value finds all the bits taken (the amortized costs: one widening is N*D/64, all of them together less than five builds), so its bitsets can be up to 1.5x that wide, and 2.5x while one widening runs

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
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps a bitset per
# node, one bit per distinct weight under it. A path a..b is O(log n) chain pieces, each O(log n) tree nodes: their
# bitsets ORed together have one bit per distinct value on the path. With D distinct values a bitset is D / 64 words, so
# this is for up to a few thousand distinct values (memory is 2 * n * D / 8 bytes). A value gets its bit the first time
# it appears, also later through an assign, and keeps it. An assign over a path or a subtree is kept at the O(log n)
# tree nodes that cover each stretch and handed down only when something below one of them is needed.
class Tree:
    # O(n * D / 64) -- builds the layout and the bitset tree; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, or an edge has no weight
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
        above = [0] * (hi + 1)  # above[v]: the weight of the edge above v (the root has none)
        for e in edges:
            above[e[0] if par[e[0]] == e[1] else e[1]] = e[2]

        # bits: a segment tree over the positions (its leaves n .. 2n - 1), each node an int used as a bitset with one
        # bit per distinct value under it; a parent is the OR of its two children. ids: each value's bit, handed out as
        # values first appear; values[b]: the value whose bit is b. tag[i]: for a leaf, the bit of its value; for a node
        # above, the bit every value under it was assigned and its children have not been told yet (-1: none).
        ids, values = {}, []
        bits, tag = [0] * (2 * n), [-1] * (2 * n)
        for i in range(1, n):
            x = above[order[i]]
            b = ids.get(x)
            if b is None:
                b = ids[x] = len(values)
                values.append(x)
            bits[n + i], tag[n + i] = 1 << b, b
        for i in range(n - 1, 0, -1):
            bits[i] = bits[2 * i] | bits[2 * i + 1]
        self.ids, self.values, self.bits, self.tag = ids, values, bits, tag

    # hands every assign waiting above leaf p down to the two children, top first
    def _push(self, p):
        bits, tag = self.bits, self.tag
        for s in range(p.bit_length() - 1, 0, -1):
            i = p >> s
            b = tag[i]
            if b >= 0:
                bits[2 * i] = bits[2 * i + 1] = 1 << b
                tag[2 * i] = tag[2 * i + 1] = b
                tag[i] = -1

    # recomputes the seg nodes above leaf p (one with an assign waiting is right as it is)
    def _pull(self, p):
        bits, tag = self.bits, self.tag
        p >>= 1
        while p:
            if tag[p] < 0:
                bits[p] = bits[2 * p] | bits[2 * p + 1]
            p >>= 1

    # the values at positions l..r all become x (nothing for an empty stretch, l > r)
    def _assign(self, l, r, x):
        if l > r:
            return
        b = self.ids.get(x)
        if b is None:
            b = self.ids[x] = len(self.values)
            self.values.append(x)
        bits, tag = self.bits, self.tag
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        i, j = l, r + 1
        while i < j:
            if i & 1:
                bits[i], tag[i] = 1 << b, b
                i += 1
            if j & 1:
                j -= 1
                bits[j], tag[j] = 1 << b, b
            i >>= 1
            j >>= 1
        self._pull(l)
        self._pull(r)

    # the bit of the value at position p: the topmost assign still waiting above its leaf, else the leaf's own
    def _bitAt(self, p):
        tag = self.tag
        p += self.n
        for s in range(p.bit_length() - 1, 0, -1):
            if tag[p >> s] >= 0:
                return tag[p >> s]
        return tag[p]

    # the bitset of the values at positions l..r (0 for an empty stretch, l > r)
    def _or(self, l, r):
        if l > r:
            return 0
        bits = self.bits
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        r += 1
        res = 0
        while l < r:
            if l & 1:
                res |= bits[l]
                l += 1
            if r & 1:
                r -= 1
                res |= bits[r]
            l >>= 1
            r >>= 1
        return res

    # the path a..b as stretches of positions (l, r), one for each chain piece
    def _pieces(self, a, b):
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        out = []
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            out.append((pos[head[a]], pos[a]))
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            out.append((l + 1, r))
        return out

    # the bitset of the edge weights on the path a..b
    def _pathBits(self, a, b):
        res = 0
        for l, r in self._pieces(a, b):
            res |= self._or(l, r)
        return res

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
        p = self.pos[self._edge("edgeGet", a, b)]
        return self.values[self._bitAt(p)]

    # O(log n * D/64) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        p = self.pos[self._edge("edgeAssign", a, b)]
        self._assign(p, p, w)

    # O(log n * D/64) -- weight(a - b) += w; a and b are the edge's two ends, in either order
    def edgeAdd(self, a, b, w):
        p = self.pos[self._edge("edgeAdd", a, b)]
        self._assign(p, p, self.values[self._bitAt(p)] + w)

    # O(log n * D/64) -- weight(a - b) = max(weight, w); a and b are the edge's two ends, in either order
    def edgeChmax(self, a, b, w):
        p = self.pos[self._edge("edgeChmax", a, b)]
        if w > self.values[self._bitAt(p)]:
            self._assign(p, p, w)

    # O(log n * D/64) -- weight(a - b) = min(weight, w); a and b are the edge's two ends, in either order
    def edgeChmin(self, a, b, w):
        p = self.pos[self._edge("edgeChmin", a, b)]
        if w < self.values[self._bitAt(p)]:
            self._assign(p, p, w)

    # O(log^2 n * D/64) -- weight = w for every edge on the path a..b
    def edgePathAssign(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAssign", a, b)
        for l, r in self._pieces(a, b):
            self._assign(l, r, w)

    # O(log^2 n * D/64) -- number of distinct edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathCountDistinct(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountDistinct", a, b)
        return bin(self._pathBits(a, b)).count("1")

    # O(log^2 n * D/64) -- are all the edge weights on the path a..b distinct?; True when a == b (no edges)
    def edgePathAllDistinct(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAllDistinct", a, b)
        return bin(self._pathBits(a, b)).count("1") == self._dist(a, b)

    # O(log n * D/64) -- weight = w for every edge in node's subtree
    def edgeSubtreeAssign(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAssign", node)
        l = self.pos[node]
        # the edges below node: the positions after its own (none for a leaf: an empty stretch)
        self._assign(l + 1, l + self.sz[node] - 1, w)

    # O(log n * D/64) -- number of distinct edge weights in node's subtree; 0 when node is a leaf (no edges)
    def edgeSubtreeCountDistinct(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountDistinct", node)
        l = self.pos[node]
        # the edges below node: the positions after its own (none for a leaf: an empty stretch)
        return bin(self._or(l + 1, l + self.sz[node] - 1)).count("1")

    # O(log n * D/64) -- are all the edge weights in node's subtree distinct?; True when node is a leaf (no edges)
    def edgeSubtreeAllDistinct(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAllDistinct", node)
        l = self.pos[node]
        # the edges below node: the positions after its own (none for a leaf: an empty stretch)
        many = bin(self._or(l + 1, l + self.sz[node] - 1)).count("1")
        return many == self.sz[node] - 1

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
