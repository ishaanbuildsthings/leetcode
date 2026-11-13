# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-leftmostIndexOf-leftmostIndexOfInRange-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostIndexOf-leftmostIndexOfInRange-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: countAtDepthInSubtree depth edgeNearestAncestorEqX edgePathFirstEqX edgePathLastEqX isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeNearestAncestorEqX nodePathFirstEqX nodePathLastEqX parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: position-trees
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeNearestAncestorEqX: log^2(N)
#   edgePathFirstEqX: log^2(N)
#   edgePathLastEqX: log^2(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeNearestAncestorEqX: log^2(N)
#   nodePathFirstEqX: log^2(N)
#   nodePathLastEqX: log^2(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(N)
# @memory:
#   layout: none
#   node: L[2*N*log(N)] R[2*N*log(N)]
#   tags: none
#   other: roots[2*N] vals[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: one dynamic seg tree over the positions per distinct value; at most about N log N nodes live at once (freed nodes are reused); values are hashed, so any values work

# One seg tree over the positions per value (mass change, CF 911G): rangeReplace(l, r, x, y) turns every x in a[l..r]
# into y in O(log N) amortized, for any values. Each distinct value keeps a seg tree over 0..n-1 holding the positions
# where it is; a change splits x's tree at [l, r] (O(log N) new nodes) and merges the cut part into y's tree (each
# step of a merge frees a node, so merges cost O(log N) amortized over the whole run). Also: where x first / last
# appears (in a range). All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.

from random import getrandbits


class PositionTrees:
    # node 0 = the empty tree; L / R: children
    __slots__ = ("n", "L", "R", "ids", "vals", "roots", "free")
    salt = getrandbits(62)  # ids' int keys are salted with this, so no fixed input can make them collide

    # O(N log N) -- arr: the initial array (a list)
    def __init__(self, arr):
        n = self.n = len(arr)
        self.L, self.R = [0], [0]
        self.ids, self.vals, self.roots, self.free = {}, [], [], []
        for i, v in enumerate(arr):
            k = self._id(v)
            self.roots[k] = self._insert(self.roots[k], i)

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(logN) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        if k is not None and x != y:
            self._move(k, l, r, y)

    # O(logN) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if L[t]:
                t, hi = L[t], mid
            else:
                t, lo = R[t], mid + 1
        return lo

    # O(logN) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        t = self.roots[k] if k is not None else 0
        if not t:
            return -1
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            if R[t]:
                t, lo = R[t], mid + 1
            else:
                t, hi = L[t], mid
        return lo

    # O(logN) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, True) if k is not None else -1

    # O(logN) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        k = self.ids.get(x ^ self.salt if type(x) is int else x)
        return self._first(self.roots[k], 0, self.n - 1, l, r, False) if k is not None else -1

    # O(N log N) -- the whole current array
    def getAll(self):
        out, L, R = [None] * self.n, self.L, self.R
        for k, t in enumerate(self.roots):
            if not t:
                continue
            v, stack = self.vals[k], [(t, 0, self.n - 1)]
            while stack:
                t, lo, hi = stack.pop()
                if lo == hi:
                    out[lo] = v
                    continue
                mid = (lo + hi) >> 1
                if L[t]:
                    stack.append((L[t], lo, mid))
                if R[t]:
                    stack.append((R[t], mid + 1, hi))
        return out

    # ---- internals ----

    def _id(self, v):  # v's index into vals / roots (a new one, with an empty tree, the first time v is seen)
        key = v ^ self.salt if type(v) is int else v
        k = self.ids.get(key)
        if k is None:
            k = self.ids[key] = len(self.vals)
            self.vals.append(v)
            self.roots.append(0)
        return k

    def _new(self):  # an empty node (a freed one if there is one)
        if self.free:
            x = self.free.pop()
            self.L[x] = self.R[x] = 0
            return x
        self.L.append(0)
        self.R.append(0)
        return len(self.L) - 1

    def _pull(self, x):  # recompute x from its children
        return x

    def _insert(self, t, i):  # t's tree with position i (not in it) added; returns the root
        root = t = t or self._new()
        L, R, lo, hi = self.L, self.R, 0, self.n - 1
        while True:
            if lo == hi:
                return root
            mid = (lo + hi) >> 1
            if i <= mid:
                if not L[t]:
                    c = self._new()
                    L[t] = c
                t, hi = L[t], mid
            else:
                if not R[t]:
                    c = self._new()
                    R[t] = c
                t, lo = R[t], mid + 1

    def _split(self, t, lo, hi, l, r):  # (t without the positions in [l, r], a tree of just those); no empty nodes left
        if not t or r < lo or hi < l:
            return t, 0
        if l <= lo and hi <= r:
            return 0, t
        L, R, mid = self.L, self.R, (lo + hi) >> 1
        a1, b1 = self._split(L[t], lo, mid, l, r)
        a2, b2 = self._split(R[t], mid + 1, hi, l, r)
        cut = 0
        if b1 or b2:
            cut = self._new()
            L[cut], R[cut] = b1, b2
            self._pull(cut)
        if a1 or a2:
            L[t], R[t] = a1, a2
            return self._pull(t), cut
        self.free.append(t)
        return 0, cut

    def _merge(self, a, b):  # the union of two trees over disjoint positions; b's nodes that overlap a's are freed
        if not a or not b:
            return a or b
        L, R = self.L, self.R
        L[a] = self._merge(L[a], L[b])
        R[a] = self._merge(R[a], R[b])
        self.free.append(b)
        return self._pull(a)

    def _move(self, k, l, r, y):  # the positions in [l, r] of vals[k]'s tree go to y's
        keep, cut = self._split(self.roots[k], 0, self.n - 1, l, r)
        self.roots[k] = keep
        if cut:
            ky = self._id(y)
            t = self.roots[ky] = self._merge(self.roots[ky], cut)

    def _first(self, t, lo, hi, l, r, left):  # the first (left) / last position of t's tree in [l, r], or -1
        if not t or r < lo or hi < l:
            return -1
        if lo == hi:
            return lo
        mid = (lo + hi) >> 1
        a, b = (self.L[t], self.R[t]) if left else (self.R[t], self.L[t])
        alo, ahi, blo, bhi = (lo, mid, mid + 1, hi) if left else (mid + 1, hi, lo, mid)
        res = self._first(a, alo, ahi, l, r, left)
        return res if res != -1 else self._first(b, blo, bhi, l, r, left)


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
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (PositionTrees)
# sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower
# end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain
# it crosses.
class Tree:
    # O(n * log n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree
    # on nodes 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
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
        self.nodeSeg = PositionTrees([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = PositionTrees(arr)  # each edge's weight, at its lower end's position

    # O(log^2 n) -- nearest ancestor of node (node included) with val = x (-1 if none)
    def nodeNearestAncestorEqX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorEqX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.nodeSeg.rightmostIndexOfInRange
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _nodeFirstEqX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.nodeSeg.leftmostIndexOfInRange, self.nodeSeg.rightmostIndexOfInRange
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] >= pos[b]:  # the piece holding the lca: b is the top
            l, r = pos[b], pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        else:
            l, r = pos[a], pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first node walking a -> b with val = x (-1 if none)
    def nodePathFirstEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstEqX", a, b)
        return self._nodeFirstEqX(a, b, x)

    # O(log^2 n) -- last node walking a -> b with val = x (-1 if none)
    def nodePathLastEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastEqX", a, b)
        return self._nodeFirstEqX(b, a, x)

    # O(log^2 n) -- nearest edge above node (toward the root) with weight = x, as its lower end (-1 if none)
    def edgeNearestAncestorEqX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeNearestAncestorEqX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.edgeSeg.rightmostIndexOfInRange
        while node != -1:
            l = pos[head[node]] or 1  # (position 0 is the root's: it holds no edge)
            if l <= pos[node]:
                i = find(l, pos[node], x)
                if i != -1:
                    return self.order[i]
            node = par[head[node]]
        return -1

    def _edgeFirstEqX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.edgeSeg.leftmostIndexOfInRange, self.edgeSeg.rightmostIndexOfInRange
        downs = []  # the chain pieces on b's side, bottom first (walked last, top first)
        while head[a] != head[b]:
            if dep[head[a]] >= dep[head[b]]:
                l, r = pos[head[a]], pos[a]
                i = last(l, r, x)
                if i != -1:
                    return order[i]
                a = par[head[a]]
            else:
                downs.append(b)
                b = par[head[b]]
        if pos[a] > pos[b]:  # the piece holding the lca (b): its edges sit after the lca's position
            l, r = pos[b] + 1, pos[a]
            i = last(l, r, x)
            if i != -1:
                return order[i]
        elif pos[a] < pos[b]:
            l, r = pos[a] + 1, pos[b]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        for d in reversed(downs):
            l, r = pos[head[d]], pos[d]
            i = first(l, r, x)
            if i != -1:
                return order[i]
        return -1

    # O(log^2 n) -- first edge walking a -> b with weight = x, as its lower end (-1 if none)
    def edgePathFirstEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstEqX", a, b)
        return self._edgeFirstEqX(a, b, x)

    # O(log^2 n) -- last edge walking a -> b with weight = x, as its lower end (-1 if none)
    def edgePathLastEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastEqX", a, b)
        return self._edgeFirstEqX(b, a, x)

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
