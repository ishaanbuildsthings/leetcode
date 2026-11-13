# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countInValRange-kthGtX-kthGteX-kthLtX-kthLteX-pointGet/template.py
# @operations: countAtDepthInSubtree depth edgeGet edgePathCountInValRange edgeSubtreeCountInValRange isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeGet nodePathCountInValRange nodeSubtreeCountInValRange parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: merge-sort-tree
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeGet: 1
#   edgePathCountInValRange: log^2(N)
#   edgeSubtreeCountInValRange: log(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeGet: 1
#   nodePathCountInValRange: log^2(N)
#   nodeSubtreeCountInValRange: log(N)
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
#   node: cnt[2*N*log(N)]
#   tags: none
#   other: sortedVals[2*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: one row of N prefix counts per level (wavelet style), no per-node lists

from bisect import bisect_left, bisect_right
from itertools import accumulate, compress
from operator import not_


class MergeSortTree:
    # Build: O(n log n) time, ceil(log2 n) * n ints of space.
    # Every query: O(log n) — one binary search at the root, then an iterative top-down walk, O(1) per level, no
    # recursion and no per-node lists.
    #
    # Same two representational choices as the C++ template:
    #   * Nodes do not store their sorted values. Fractional cascading only ever
    #     binary searches the root, so only sortedVals is kept. A node's element
    #     count is tr - tl + 1, which the walk already tracks.
    #   * cnt is one row per depth. At any depth the segment tree nodes partition
    #     [0, n-1], and a node covering [tl, tr] owns exactly working-array slots
    #     tl..tr, so (depth, tl) addresses a node's prefix data with no offset
    #     table and no node index at all.
    #
    # Divergences from the C++, all forced by CPython:
    #   * cnt is a list of per-depth rows rather than one flat array with d * n
    #     offsets — same addressing, one less multiply per access.
    #   * leftCount is inlined at every use. As a method it would be ~34 calls
    #     per query and would dominate the query cost.
    #   * A size-2 node is special-cased in the build: both its children are
    #     leaves, so it needs no partition and no scratch writes. Saves half the
    #     internal nodes. In C++ this is noise; here it is worth ~20% of the build.
    #   * sorted() instead of a radix sort — sorted() is already C, and a radix
    #     written in Python bytecode would be far slower.
    def __init__(self, arr):
        self.arr = arr
        self.n = n = len(arr)
        self.levels = levels = 0
        self.sortedVals = sorted(arr)  # root's sorted values — the only list ever binary-searched
        # cnt[d][tl + j] = # of the first (j+1) elements of the depth-d node starting at tl that live in its left child
        self.cnt = cnt = []
        if n == 0:
            return
        width = 1
        while width < n:
            width <<= 1
            levels += 1
        self.levels = levels

        # Splitting a value-ordered index list on "index <= mid" preserves the ordering, so each level is one stable
        # partition per node — all C-level, no merging.
        cur = sorted(range(n), key=arr.__getitem__)  # indices by value, ties by index — same tie rule as L[li] <= R[ri]
        buf = cur[:]
        nodes = [(0, n - 1)]
        for d in range(levels):
            row = [0] * n
            nxt = []
            addChild = nxt.append
            for tl, tr in nodes:
                span = tr - tl
                if span == 0:
                    continue
                if span == 1:
                    # both children are leaves, so they need no cnt row of their own and this node's two entries are
                    # fully determined by which of the two indices sorted first
                    if cur[tl] == tl:
                        row[tl] = 1
                    row[tr] = 1
                    continue
                mid = (tl + tr) >> 1
                seg = cur[tl:tr + 1]
                goesLeft = list(map(mid.__ge__, seg))  # True where index <= mid
                row[tl:tr + 1] = accumulate(goesLeft)
                buf[tl:mid + 1] = compress(seg, goesLeft)
                buf[mid + 1:tr + 1] = compress(seg, map(not_, goesLeft))
                addChild((tl, mid))
                addChild((mid + 1, tr))
            cnt.append(row)
            cur, buf = buf, cur
            nodes = nxt

    # --- count ---

    # O(log n) — count elements >= x in [ql, qr]
    # Seeded with bisect_left (elements < x) and complemented against the range size.
    # The walk is inlined rather than shared with countLteX: a countPrefix call per query is measurable in CPython, and
    # it is not in C++.
    def countGteX(self, ql, qr, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr:
            return 0
        total = qr - ql + 1
        p = bisect_left(self.sortedVals, x)
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return total - p
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break
        res = 0

        # left boundary: cover [ql, mid] inside the left child
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                res += pa - lp  # entire right child is inside [ql, qr]
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        res += pa

        # right boundary: cover [mid + 1, qr] inside the right child
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                res += lp  # entire left child is inside [ql, qr]
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        return total - (res + pa)

    # O(log n) — count elements <= x in [ql, qr]
    # Walk inlined, see countGteX
    def countLteX(self, ql, qr, x):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr:
            return 0
        p = bisect_right(self.sortedVals, x)
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return p
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break
        res = 0

        # left boundary: cover [ql, mid] inside the left child
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                res += pa - lp  # entire right child is inside [ql, qr]
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        res += pa

        # right boundary: cover [mid + 1, qr] inside the right child
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                res += lp  # entire left child is inside [ql, qr]
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        return res + pa

    # O(log n) — count elements in value range [valLow, valHigh] (inclusive) in index range [ql, qr]; needs
    # 0 <= ql <= qr < n, else IndexError
    def countInValRange(self, ql, qr, valLow, valHigh):
        if not 0 <= ql <= qr < self.n:
            raise IndexError(f"countInValRange: needs 0 <= ql <= qr < n, got ql = {ql}, qr = {qr}, n = {self.n}")
        ql, qr = max(ql, 0), min(qr, self.n - 1)
        if ql > qr or valHigh < valLow:
            return 0
        # (<= valHigh) - (< valLow), with "< valLow" as the range minus ">= valLow": no valLow - 1, so any values work
        return self.countLteX(ql, qr, valHigh) - (qr - ql + 1 - self.countGteX(ql, qr, valLow))

    # --- find k-th by position ---

    # Same decomposition as countPrefix, but returns the canonical nodes in
    # LEFT-TO-RIGHT order as (d, tl, tr, p). At most 2 * levels + 2 of them.
    # Only findKth* needs this; the counting path stays allocation-free.
    def decompose(self, ql, qr, p):
        cnt = self.cnt
        tl, tr, d = 0, self.n - 1, 0
        while True:
            if ql <= tl and tr <= qr:
                return [(d, tl, tr, p)]
            mid = (tl + tr) >> 1
            row = cnt[d]
            leftP = row[tl + p - 1] if p else 0
            if qr <= mid:
                tr = mid
                p = leftP
                d += 1
            elif ql > mid:
                tl = mid + 1
                p -= leftP
                d += 1
            else:
                break

        # left walk collects right-to-left (the node it lands on is the leftmost), so reverse
        leftParts = []
        a, b, pa, da = tl, mid, leftP, d + 1
        while a < b and ql > a:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if ql <= m:
                leftParts.append((da + 1, m + 1, b, pa - lp))
                b = m
                pa = lp
            else:
                a = m + 1
                pa -= lp
            da += 1
        leftParts.append((da, a, b, pa))
        parts = leftParts[::-1]

        # right walk already collects left-to-right
        a, b, pa, da = mid + 1, tr, p - leftP, d + 1
        while a < b and qr < b:
            m = (a + b) >> 1
            row = cnt[da]
            lp = row[a + pa - 1] if pa else 0
            if qr > m:
                parts.append((da + 1, a, m, lp))
                a = m + 1
                pa -= lp
            else:
                b = m
                pa = lp
            da += 1
        parts.append((da, a, b, pa))
        return parts

    # O(log n) — array index (POSITION, not value) of the k-th element >= x in
    # [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    # k-th (1-indexed, left to right) i in [ql, qr] NOT among the p0 globally-smallest values
    def _kthAbove(self, ql, qr, k, p0):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, p0):
            gteInNode = (tr - tl + 1) - p
            if k > gteInNode:
                k -= gteInNode
                continue
            while tl < tr:
                mid = (tl + tr) >> 1
                row = cnt[d]
                lp = row[tl + p - 1] if p else 0
                leftGte = (mid - tl + 1) - lp
                if k <= leftGte:
                    tr = mid
                    p = lp
                else:
                    k -= leftGte
                    tl = mid + 1
                    p -= lp
                d += 1
            return tl
        return -1

    # O(log n) — array index (POSITION, not value) of the k-th element <= x in
    # [ql, qr], 1-indexed k, scanning left to right. Returns -1 if fewer than k exist.
    # k-th (1-indexed, left to right) i in [ql, qr] among the p0 globally-smallest values
    def _kthBelow(self, ql, qr, k, p0):
        if ql < 0:
            ql = 0
        if qr > self.n - 1:
            qr = self.n - 1
        if ql > qr or k <= 0:
            return -1
        cnt = self.cnt
        for d, tl, tr, p in self.decompose(ql, qr, p0):
            if k > p:
                k -= p
                continue
            while tl < tr:
                mid = (tl + tr) >> 1
                row = cnt[d]
                lp = row[tl + p - 1] if p else 0
                if k <= lp:
                    tr = mid
                    p = lp
                else:
                    k -= lp
                    tl = mid + 1
                    p -= lp
                d += 1
            return tl
        return -1

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] >= x, or -1; needs
    # 0 <= ql <= qr < n, else IndexError
    def kthGteX(self, ql, qr, k, x):
        if not 0 <= ql <= qr < self.n:
            raise IndexError(f"kthGteX: needs 0 <= ql <= qr < n, got ql = {ql}, qr = {qr}, n = {self.n}")
        return self._kthAbove(ql, qr, k, bisect_left(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] > x, or -1; needs
    # 0 <= ql <= qr < n, else IndexError
    def kthGtX(self, ql, qr, k, x):
        if not 0 <= ql <= qr < self.n:
            raise IndexError(f"kthGtX: needs 0 <= ql <= qr < n, got ql = {ql}, qr = {qr}, n = {self.n}")
        return self._kthAbove(ql, qr, k, bisect_right(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] <= x, or -1; needs
    # 0 <= ql <= qr < n, else IndexError
    def kthLteX(self, ql, qr, k, x):
        if not 0 <= ql <= qr < self.n:
            raise IndexError(f"kthLteX: needs 0 <= ql <= qr < n, got ql = {ql}, qr = {qr}, n = {self.n}")
        return self._kthBelow(ql, qr, k, bisect_right(self.sortedVals, x))

    # O(logN) -- index of the k-th (1-indexed, left to right) i in [ql, qr] with a[i] < x, or -1; needs
    # 0 <= ql <= qr < n, else IndexError
    def kthLtX(self, ql, qr, k, x):
        if not 0 <= ql <= qr < self.n:
            raise IndexError(f"kthLtX: needs 0 <= ql <= qr < n, got ql = {ql}, qr = {qr}, n = {self.n}")
        return self._kthBelow(ql, qr, k, bisect_left(self.sortedVals, x))

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        return self.arr[i]


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
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (MergeSortTree)
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
        self.nodeSeg = MergeSortTree([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = MergeSortTree(arr)  # each edge's weight, at its lower end's position

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(log^2 n) -- how many node values on the path a..b are in [low, high]
    def nodePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, low, high)
        return res

    # O(log n) -- how many node values in node's subtree are in [low, high]
    def nodeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountInValRange", node)
        l = self.pos[node]
        return self.nodeSeg.countInValRange(l, l + self.sz[node] - 1, low, high)

    # the position that holds the edge a - b: its lower end's (a and b in either order)
    def _edge(self, name, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad(name, a, b)
        if self.par[a] == b:
            return self.pos[a]
        if self.par[b] == a:
            return self.pos[b]
        raise IndexError(f"{name}: needs an edge between a and b, got {a} and {b}")

    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        return self.edgeSeg.pointGet(self._edge("edgeGet", a, b))

    # O(log^2 n) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    def edgePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountInValRange", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countInValRange
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], low, high)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, low, high)
        return res

    # O(log n) -- how many edge weights in node's subtree are in [low, high]; 0 when node is a leaf (no edges)
    def edgeSubtreeCountInValRange(self, node, low, high):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountInValRange", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countInValRange(l, r, low, high)

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
