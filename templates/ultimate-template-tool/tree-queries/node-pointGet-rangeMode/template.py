# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-pointGet-rangeMode/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointGet-rangeMode/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeGet nodeSubtreeMode parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: sqrt
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
#   nodeGet: 1
#   nodeSubtreeMode: sqrt(N)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*sqrt(N)
# @memory:
#   layout: none
#   node: blockMode[1*N] blockCnt[1*N]
#   tags: none
#   other: comp[1*N] positions[1*N] posIdx[1*N] vals[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: blockMode/blockCnt are (N/B)^2 = N tables with B = sqrt(N); vals is the distinct values


# ========================
# COMPLEXITIES

# O(n root n) build time, O(n) memory

# O(rootN) rangeMode(l, r) -> (mode, frequency)

# ========================
"""
How do range mode work in rootN?

First, we split the array into rootN blocks. I want to be able to answer: "what is the mode from bl...br and how many
time does it occur)
This is easy, from the starting point of each block sweep to the end of the array, every time we hit the end of the
block we know the mode for bl...some other block and we store the answer. We do rootN sweeps each N time.

Now I claim in a rangeMode(l, r) query, the mode is one of:
-the mode JUST inside the full blocks portion
-any one of the partial values

It wouldn't be possible for a value to be the mode if it's not a partial and not the mode of the full region.

We can find the mode of just the inside full blocks portion since we precomputed it.

Now we want to know for each partial, how many times does it occur in the full region? We could do this with NrootN
memory by, for each value, computing a prefix sum of size rootN, like for each block. But we can do N memory:

Map all values -> indices, and also an index to its position in that index bucket, so [5, 2, 5] has:

5 : [0, 2]
2 : [1]

But also 0->0, 1->1, 2->1 as the global index -> inside bucket index, mapping.

Now for any partial value we can find exactly where it occurs in its indices list in O(1). We then jump ahead by
modeMiddleFrequency spots and check if the ending spot is <= qr or not.
"""

# ========================


from bisect import bisect_left
from itertools import groupby, repeat
from math import isqrt


class RangeMode:
    __slots__ = ("arr", "n", "B", "numBlocks", "vals", "comp", "positions", "posIdx", "blockMode", "blockCnt")

    # O(n root n)
    def __init__(self, arr):
        self.arr = arr
        self.n = n = len(arr)
        self.B = B = max(1, isqrt(n))
        self.numBlocks = numBlocks = (n + B - 1) // B

        # coordinate compress so counting can use a flat list (by sorting, so no value is ever hashed)
        self.vals = vals = [val for val, _ in groupby(sorted(arr))]
        self.comp = comp = list(map(bisect_left, repeat(vals), arr))

        # positions[valId] = sorted indices holding valId
        # posIdx[i] = where index i sits inside positions[comp[i]]
        self.positions = positions = [[] for _ in range(len(self.vals))]
        self.posIdx = posIdx = [0] * n
        for i, valId in enumerate(comp):
            posIdx[i] = len(positions[valId])
            positions[valId].append(i)

        # blockMode[startBlock * numBlocks + endBlock] = mode (compressed id) of those blocks
        # blockCnt[...] = its frequency
        self.blockMode = blockMode = [0] * (numBlocks * numBlocks)
        self.blockCnt = blockCnt = [0] * (numBlocks * numBlocks)
        cnt = [0] * len(self.vals)
        for startBlock in range(numBlocks):
            best = 0
            bestVal = 0
            row = startBlock * numBlocks
            for endBlock in range(startBlock, numBlocks):
                for i in range(endBlock * B, min(n, (endBlock + 1) * B)):
                    valId = comp[i]
                    cnt[valId] += 1
                    if cnt[valId] > best:
                        best = cnt[valId]
                        bestVal = valId
                blockMode[row + endBlock] = bestVal
                blockCnt[row + endBlock] = best
            # reset only what we touched
            for i in range(startBlock * B, n):
                cnt[comp[i]] = 0

    #################### PUBLIC METHODS START HERE ####################

    # O(rootN) -- (mode, frequency) of arr[l...r] inclusive. requires needs 0 <= l <= r < n, else IndexError ties:
    # returns any one of the tied values
    def rangeMode(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeMode: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        B = self.B
        comp = self.comp
        positions = self.positions
        posIdx = self.posIdx
        leftBlock = l // B
        rightBlock = r // B

        if rightBlock - leftBlock <= 1:
            # no whole middle block, every element is a candidate
            best = 0
            bestVal = comp[l]
            leftEdgeEnd = r
            rightEdgeStart = r + 1
        else:
            idx = (leftBlock + 1) * self.numBlocks + (rightBlock - 1)
            best = self.blockCnt[idx]
            bestVal = self.blockMode[idx]
            leftEdgeEnd = (leftBlock + 1) * B - 1
            rightEdgeStart = rightBlock * B

        # left edge: is the (best + 1)-th copy counting forward from here still <= r?
        for i in range(l, leftEdgeEnd + 1):
            valId = comp[i]
            plist = positions[valId]
            k = posIdx[i]
            while k + best < len(plist) and plist[k + best] <= r:
                best += 1
                bestVal = valId

        # right edge: is the (best + 1)-th copy counting backward from here still >= l?
        for i in range(rightEdgeStart, r + 1):
            valId = comp[i]
            plist = positions[valId]
            k = posIdx[i]
            while k - best >= 0 and plist[k - best] >= l:
                best += 1
                bestVal = valId

        return self.vals[bestVal], best

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]


from bisect import bisect_left


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
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above (RangeMode)
# in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it crosses.
class Tree:
    # O(n * sqrt(n)) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or vals has the wrong length
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
        self.seg = RangeMode([vals[v] for v in order])  # the values, in position order

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.seg.pointGet(self.pos[node])

    # O(sqrt(n)) -- (mode, frequency) of the node values in node's subtree
    def nodeSubtreeMode(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeMode", node)
        l = self.pos[node]
        return self.seg.rangeMode(l, l + self.sz[node] - 1)

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
