# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndQuery-rangeOrQuery-rangeSum-rangeXorApply/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathAND nodePathOR nodePathSum nodePathXORApply nodeSubtreeAND nodeSubtreeOR nodeSubtreeSum nodeSubtreeXORApply parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: lazy-seg-tree
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
#   nodeAdd: log(N)*log(U)
#   nodeAssign: log(N)*log(U)
#   nodeChmax: log(N)*log(U)
#   nodeChmin: log(N)*log(U)
#   nodeGet: log(N)*log(U)
#   nodePathAND: log^2(N)*log(U)
#   nodePathOR: log^2(N)*log(U)
#   nodePathSum: log^2(N)*log(U)
#   nodePathXORApply: log^2(N)*log(U)
#   nodeSubtreeAND: log(N)*log(U)
#   nodeSubtreeOR: log(N)*log(U)
#   nodeSubtreeSum: log(N)*log(U)
#   nodeSubtreeXORApply: log(N)*log(U)
#   parent: 1
#   parentRootedAt: log(N)
#   pathIntersection: log(N)
#   pathNodes: K+log(N)
#   subtreeSize: 1
#   subtreeSizeRootedAt: log(N)
#   unweightedDist: log(N)
#   unweightedDistBetweenPaths: log(N)
#   unweightedDistToPath: log(N)
#   build: N*log(U)
# @memory:
#   layout: 2n-iterative
#   node: cnt[2*N*log(U)]
#   tags: xorTag[1*N]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: cnt keeps, per node and per bit, how many values below have that bit set (bits = log U, 20 by default); tags live on internal nodes only

# Range xor= with range sum / and / or queries, plus point ops. All indices 0-based, ranges inclusive.
# Values live in [0, 2^bits). Each node counts, for every bit, how many of its values have that bit set. A xor X
# flips the bits set in X: per bit, a flip turns the count c into length - c, so the tag is just the mask to
# flip (this is BitCountTree without the AND tag that only and= / or= need).
# So every update is an ordinary lazy tag, a true O(log N * bits) with no amortization (unlike bitwise beats, which
# cannot apply xor to a node whose values disagree on a bit). Sum = sum over bits of count * 2^bit.
# Iterative 2N lazy tree; a covering node at level s is a perfect subtree of 2^s leaves.


class BitCountTree:
    __slots__ = ("n", "h", "bits", "full", "cnt", "xorTag")

    # O(N * bits)
    def __init__(self, arr, bits=20):
        n = self.n = len(arr)
        self.h = n.bit_length()
        self.bits = bits
        full = self.full = (1 << bits) - 1
        cnt = self.cnt = [[0] * (2 * n) for _ in range(bits)]  # cnt[b][x] = # of values under node x with bit b set
        for i, v in enumerate(arr):
            for b in range(bits):
                if v >> b & 1:
                    cnt[b][n + i] = 1
        for c in cnt:
            for x in range(n - 1, 0, -1):
                c[x] = c[2 * x] + c[2 * x + 1]
        self.xorTag = [0] * n  # tags on internal nodes only

    # v -> v ^ xr on node x, which covers k slots
    def _apply(self, x, k, xr):
        for b in range(self.bits):
            c = self.cnt[b]
            if xr >> b & 1:
                c[x] = k - c[x]
        if x < self.n:
            self.xorTag[x] ^= xr

    def _push(self, p):
        full = self.full
        for s in range(self.h, 0, -1):
            x = p >> s
            xr = self.xorTag[x]
            if xr:
                k = 1 << (s - 1)
                self._apply(2 * x, k, xr)
                self._apply(2 * x + 1, k, xr)
                self.xorTag[x] = 0

    def _rebuild(self, p):
        k = 1
        while p > 1:
            p >>= 1
            k <<= 1
            xr = self.xorTag[p]
            for b in range(self.bits):
                c = self.cnt[b]
                v = c[2 * p] + c[2 * p + 1]
                if xr >> b & 1:
                    v = k - v
                c[p] = v

    def _update(self, l, r, xr):
        if l > r:
            return
        l0, r0 = l + self.n, r + self.n
        self._push(l0)
        self._push(r0)
        i, j, k = l0, r0 + 1, 1
        while i < j:
            if i & 1:
                self._apply(i, k, xr)
                i += 1
            if j & 1:
                j -= 1
                self._apply(j, k, xr)
            i >>= 1
            j >>= 1
            k <<= 1
        self._rebuild(l0)
        self._rebuild(r0)

    # the canonical nodes of [l, r] with their lengths, after pushing the two boundary paths
    def _nodes(self, l, r):
        l += self.n
        r += self.n
        self._push(l)
        self._push(r)
        out, k = [], 1
        r += 1
        while l < r:
            if l & 1:
                out.append((l, k))
                l += 1
            if r & 1:
                r -= 1
                out.append((r, k))
            l >>= 1
            r >>= 1
            k <<= 1
        return out

    # O(logN * bits) -- a[i] ^= X for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeXorApply(self, l, r, X):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeXorApply: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        self._update(l, r, X & self.full)

    # O(logN * bits) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeSum(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeSum: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return 0
        nodes = self._nodes(l, r)
        return sum(sum(self.cnt[b][x] for x, _ in nodes) << b for b in range(self.bits))

    # O(logN * bits) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeAndQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAndQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if all(self.cnt[b][x] == k for x, k in nodes))

    # O(logN * bits) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else IndexError
    def rangeOrQuery(self, l, r):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeOrQuery: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        nodes = self._nodes(l, r)
        return sum(1 << b for b in range(self.bits) if any(self.cnt[b][x] for x, _ in nodes))

    # O(logN * bits) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        return sum(self.cnt[b][p] << b for b in range(self.bits))

    # O(N * logU) -- the whole array: push every tag down one level at a time from the root (the nodes s levels above
    # the leaves are (n >> s) .. ((2n - 1) >> s); their children cover k = 1 << (s - 1) leaves), then read the leaves
    def getAll(self):
        n, full = self.n, self.full
        for s in range(self.h, 0, -1):
            k = 1 << (s - 1)
            for x in range(max(1, n >> s), ((2 * n - 1) >> s) + 1):
                xr = self.xorTag[x]
                if xr:
                    self._apply(2 * x, k, xr)
                    self._apply(2 * x + 1, k, xr)
                    self.xorTag[x] = 0
        cnt = self.cnt
        return [sum(cnt[b][p] << b for b in range(self.bits)) for p in range(n, 2 * n)]

    # O(logN * bits) -- a[i] = val & FULL; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        p = i + self.n
        self._push(p)
        val &= self.full
        for b in range(self.bits):
            self.cnt[b][p] = val >> b & 1
        self._rebuild(p)

    # O(logN * bits) -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(logN * bits) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(logN * bits) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)

    # O(log(N)*log(U)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else raises IndexError
    def sumAll(self):
        if self.n < 1:
            raise IndexError("sumAll: needs n >= 1")
        return self.rangeSum(0, self.n - 1)

    # O(log(N)*log(U)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else raises
    # IndexError
    def andAll(self):
        if self.n < 1:
            raise IndexError("andAll: needs n >= 1")
        return self.rangeAndQuery(0, self.n - 1)

    # O(log(N)*log(U)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else raises IndexError
    def orAll(self):
        if self.n < 1:
            raise IndexError("orAll: needs n >= 1")
        return self.rangeOrQuery(0, self.n - 1)


from bisect import bisect_left


# tree = Tree(edges, root, vals, bits)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
# bits: values live in [0, 2^bits).
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30], bits)       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30], bits)    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: one heavy-light pass gives every node a position, so that each heavy chain and each subtree is one
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
# (BitCountTree) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain it
# crosses.
class Tree:
    # O(n * log U) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or vals has the wrong length
    def __init__(self, edges, root, vals, bits=20):
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
        self.seg = BitCountTree([vals[v] for v in order], bits)  # the values, in position order

    # O(log n * log U) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.seg.pointGet(self.pos[node])

    # O(log n * log U) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.seg.pointAssign(self.pos[node], x)

    # O(log n * log U) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.seg.pointAdd(self.pos[node], x)

    # O(log n * log U) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.seg.pointChmax(self.pos[node], x)

    # O(log n * log U) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.seg.pointChmin(self.pos[node], x)

    # O(log^2 n * log U) -- val ^= x for every node on the path a..b
    def nodePathXORApply(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathXORApply", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.rangeXorApply
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, x) if l <= r else apply(r, l, x)

    # O(log^2 n * log U) -- sum of the node values on the path a..b
    def nodePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSum", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeSum
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r)
        return res

    # O(log^2 n * log U) -- AND of the node values on the path a..b
    def nodePathAND(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAND", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeAndQuery
        res = -1
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res &= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res &= query(l, r)
        return res

    # O(log^2 n * log U) -- OR of the node values on the path a..b
    def nodePathOR(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathOR", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.rangeOrQuery
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res |= query(pos[head[a]], pos[a])
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res |= query(l, r)
        return res

    # O(log n * log U) -- val ^= x for every node in node's subtree
    def nodeSubtreeXORApply(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeXORApply", node)
        l = self.pos[node]
        self.seg.rangeXorApply(l, l + self.sz[node] - 1, x)

    # O(log n * log U) -- sum of the node values in node's subtree
    def nodeSubtreeSum(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeSum", node)
        l = self.pos[node]
        return self.seg.rangeSum(l, l + self.sz[node] - 1)

    # O(log n * log U) -- AND of the node values in node's subtree
    def nodeSubtreeAND(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAND", node)
        l = self.pos[node]
        return self.seg.rangeAndQuery(l, l + self.sz[node] - 1)

    # O(log n * log U) -- OR of the node values in node's subtree
    def nodeSubtreeOR(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeOR", node)
        l = self.pos[node]
        return self.seg.rangeOrQuery(l, l + self.sz[node] - 1)

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
