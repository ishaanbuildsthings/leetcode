# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/generic-trees/GenericLazyTreeEdges.norev.py
from bisect import bisect_left

# an edge's raw weight, e.g. int, str, tuple, ...
EdgeVal = int

# what a stretch of edges is summed up as. Can replace this tuple with an entire class and it works
EdgeData = tuple

# a pending update to every edge of a stretch, e.g. add
# We never need to worry about initializing empty tags or anything, these tags come in via the update calls or when
# pushed down from parents
EdgeTag = int


# the data of one edge (a and b: its two ends, a the one nearer the root)
def edgeLeaf(w: EdgeVal, a: int, b: int) -> EdgeData:
    # return (w, w, 1)
    pass


# two stretches joined: left's edges, then right's
def edgeCombine(left: EdgeData, right: EdgeData) -> EdgeData:
    # return (left[0] + right[0], min(left[1], right[1]), left[2] + right[2])
    pass


# return new data: this data after tag is applied to it. This function is never called with a tag that never existed,
# but tags can have things like pending false values or pending no-ops (for instance two lazy bools canceling) and we
# still need to check for this and no-op (could just return the original data)
def edgeApply(data: EdgeData, tag: EdgeTag) -> EdgeData:
    # return (data[0] + tag * data[2], data[1] + tag, data[2])
    pass


# a tag that is the old tag, then the new tag
def edgeCompose(old: EdgeTag, newer: EdgeTag) -> EdgeTag:
    # return old + newer
    pass


# A lazy segment tree with no identity value: a slot that covers nothing holds None, and a slot with no tag waiting
# holds _NO_TAG. data: one item per leaf, in order
class _LazySeg:
    _NO_TAG = object()  # (so any tag value works, None too)

    def __init__(self, data, combine, apply, compose):
        self.n = n = len(data)
        self.cap = cap = 1 << max(0, (n - 1).bit_length())
        self.lg = cap.bit_length() - 1
        self.combine, self.apply, self.compose = combine, apply, compose
        # (None: a slot over the padding past n only)
        self.t = t = [None] * cap + data + [None] * (cap - n)
        # lz[k]: the tag waiting for slot k's two children
        self.lz = [_LazySeg._NO_TAG] * cap
        for k in range(cap - 1, 0, -1):
            t[k] = t[2 * k] if t[2 * k + 1] is None else combine(t[2 * k], t[2 * k + 1])

    def _applyAt(self, k, tag):
        t = self.t
        if t[k] is None:
            return
        t[k] = self.apply(t[k], tag)
        if k < self.cap:
            lz = self.lz
            lz[k] = tag if lz[k] is _LazySeg._NO_TAG else self.compose(lz[k], tag)

    def _push(self, k):
        tag = self.lz[k]
        if tag is not _LazySeg._NO_TAG:
            self._applyAt(2 * k, tag)
            self._applyAt(2 * k + 1, tag)
            self.lz[k] = _LazySeg._NO_TAG

    def _pull(self, k):
        t = self.t
        t[k] = t[2 * k] if t[2 * k + 1] is None else self.combine(t[2 * k], t[2 * k + 1])

    # hands down the tags above the leaf range [l, r) (l and r already offset by cap)
    def _pushAbove(self, l, r):
        for i in range(self.lg, 0, -1):
            if (l >> i) << i != l:
                self._push(l >> i)
            if (r >> i) << i != r:
                self._push((r - 1) >> i)

    # the data of item i
    def get(self, i):
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        return self.t[k]

    # item i becomes data
    def set(self, i, data):
        k = self.cap + i
        for j in range(self.lg, 0, -1):
            self._push(k >> j)
        self.t[k] = data
        for j in range(1, self.lg + 1):
            self._pull(k >> j)

    # items l..r joined in order (needs l <= r)
    def query(self, l, r):
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        t, combine = self.t, self.combine
        sl = sr = None
        while l < r:
            if l & 1:
                sl = t[l] if sl is None else combine(sl, t[l])
                l += 1
            if r & 1:
                r -= 1
                sr = t[r] if sr is None else combine(t[r], sr)
            l >>= 1
            r >>= 1
        if sl is None:
            return sr
        if sr is None:
            return sl
        return combine(sl, sr)

    # tag applied to every one of items l..r (needs l <= r)
    def update(self, l, r, tag):
        l += self.cap
        r += self.cap + 1
        self._pushAbove(l, r)
        a, b = l, r
        while a < b:
            if a & 1:
                self._applyAt(a, tag)
                a += 1
            if b & 1:
                b -= 1
                self._applyAt(b, tag)
            a >>= 1
            b >>= 1
        for i in range(1, self.lg + 1):
            if (l >> i) << i != l:
                self._pull(l >> i)
            if (r >> i) << i != r:
                self._pull((r - 1) >> i)


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
# between a and b, and a subtree covers the edges below node. A query with no edges to join (the path from a node to
# itself, the edges below a leaf) raises IndexError: there is no identity value to return. An update there does nothing.
# Nodes go in and come out with your labels, -1 means "none", and a label that is not in the tree raises IndexError.
# Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). A segment tree over the positions keeps, for each of its
# slots, the data of the edges under it joined in position order (an edge sits at its lower end's position, so the
# root's position holds none and the edges are items 0 .. n - 2). A subtree is one stretch, and a path a..b is O(log n)
# stretches, one per chain it crosses. Nothing here needs an identity value: a slot that covers nothing is marked as
# such and left out, and a path's pieces are joined starting from the first one; a tag waits at the O(log n) slots that
# cover a stretch until something below one of them is needed, and a slot with no tag waiting is marked as such too.
class Tree:
    # O(n) -- builds the layout and the segment tree; raises ValueError when the edges are not one tree on nodes 0..n-1
    # or 1..n, or an edge has no weight
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
        above = [None] * (hi + 1)  # above[v]: the weight of the edge above v (the root has none)
        for e in edges:
            above[e[0] if par[e[0]] == e[1] else e[1]] = e[2]
        # the edge above the node at position p is item p - 1 (position 0 is the root: no edge)
        self.edgeSeg = _LazySeg([edgeLeaf(above[v], par[v], v) for v in order[1:]], edgeCombine, edgeApply, edgeCompose)

    # the lower end of the edge a - b, the node its weight is kept under (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return a
        if self.par[b] == a:
            return b
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(log n) -- the data of the edge a - b alone; a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        v = self._edge("edgeGet", a, b)
        return self.edgeSeg.get(self.pos[v] - 1)

    # O(log n) -- the weight of the edge a - b becomes w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        v = self._edge("edgeAssign", a, b)
        self.edgeSeg.set(self.pos[v] - 1, edgeLeaf(w, self.par[v], v))

    # O(log n) -- tag applied to the edge a - b; a and b are the edge's two ends, in either order
    def edgeUpdate(self, a, b, tag):
        v = self._edge("edgeUpdate", a, b)
        p = self.pos[v] - 1
        self.edgeSeg.update(p, p, tag)

    # O(log^2 n) -- the data of the edges on the path a..b; raises IndexError when a == b (no edges)
    def edgePathQuery(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathQuery", a, b)
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        query = self.edgeSeg.query
        res = None
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                piece = query(l - 1, r - 1)
                res = piece if res is None else edgeCombine(res, piece)
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            piece = query(l - 1, r - 1)
            res = piece if res is None else edgeCombine(res, piece)
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            piece = query(l - 1, r - 1)
            res = piece if res is None else edgeCombine(res, piece)
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            piece = query(l - 1, r - 1)
            res = piece if res is None else edgeCombine(res, piece)
        if res is None:
            raise IndexError(f"edgePathQuery: needs a != b (a path from a node to itself has no edges), "
                             f"got a = b = {a}")
        return res

    # O(log^2 n) -- tag applied to every one of the edges on the path a..b (nothing when a == b)
    def edgePathUpdate(self, a, b, tag):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathUpdate", a, b)
        head, par, dep, pos = self.head, self.par, self.dep, self.pos
        update = self.edgeSeg.update
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            update(pos[head[a]] - 1, pos[a] - 1, tag)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            update(l, r - 1, tag)

    # O(log n) -- the data of the edges below node; raises IndexError when node is a leaf (no edges)
    def edgeSubtreeQuery(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeQuery", node)
        l = self.pos[node]
        if self.sz[node] == 1:
            raise IndexError(f"edgeSubtreeQuery: node {node} is a leaf, so there are no edges below it")
        return self.edgeSeg.query(l, l + self.sz[node] - 2)

    # O(log n) -- tag applied to every edge below node (nothing when node is a leaf)
    def edgeSubtreeUpdate(self, node, tag):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeUpdate", node)
        l = self.pos[node]
        if self.sz[node] > 1:
            self.edgeSeg.update(l, l + self.sz[node] - 2, tag)

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
