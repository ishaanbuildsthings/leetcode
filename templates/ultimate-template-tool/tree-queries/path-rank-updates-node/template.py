# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-rank-updates-node/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodePathCountGtX nodePathCountGteX nodePathCountInValRange nodePathCountLtX nodePathCountLteX nodePathCountOccurrences nodePathKthLargest nodePathKthSmallest nodePathLargestLtX nodePathLargestLteX nodePathMax nodePathMin nodePathSmallestGtX nodePathSmallestGteX nodePathSum nodePathSumAbsDiffToMedian nodePathSumAbsDiffToX nodePathSumGtX nodePathSumGteX nodePathSumInValRange nodePathSumKthLargestRange nodePathSumKthSmallestRange nodePathSumLargestK nodePathSumLtX nodePathSumLteX nodePathSumSmallestK parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: persistent-paths
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
#   nodeGet: 1
#   nodePathCountGtX: log(N)*log(U)
#   nodePathCountGteX: log(N)*log(U)
#   nodePathCountInValRange: log(N)*log(U)
#   nodePathCountLtX: log(N)*log(U)
#   nodePathCountLteX: log(N)*log(U)
#   nodePathCountOccurrences: log(N)*log(U)
#   nodePathKthLargest: log(N)*log(U)
#   nodePathKthSmallest: log(N)*log(U)
#   nodePathLargestLtX: log(N)*log(U)
#   nodePathLargestLteX: log(N)*log(U)
#   nodePathMax: log(N)*log(U)
#   nodePathMin: log(N)*log(U)
#   nodePathSmallestGtX: log(N)*log(U)
#   nodePathSmallestGteX: log(N)*log(U)
#   nodePathSum: log(N)*log(U)
#   nodePathSumAbsDiffToMedian: log(N)*log(U)
#   nodePathSumAbsDiffToX: log(N)*log(U)
#   nodePathSumGtX: log(N)*log(U)
#   nodePathSumGteX: log(N)*log(U)
#   nodePathSumInValRange: log(N)*log(U)
#   nodePathSumKthLargestRange: log(N)*log(U)
#   nodePathSumKthSmallestRange: log(N)*log(U)
#   nodePathSumLargestK: log(N)*log(U)
#   nodePathSumLtX: log(N)*log(U)
#   nodePathSumLteX: log(N)*log(U)
#   nodePathSumSmallestK: log(N)*log(U)
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
#   layout: none
#   node: lc[1*N*log(U)] rc[1*N*log(U)] cnt[1*N*log(U)] tot[1*N*log(U)]
#   tags: none
#   other: top[1*N] ver[1*N] val[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: U = valHi - valLo + 1. On top of the sizes above, every update adds up to 4*log(N)*log(U) nodes to lc / rc / cnt / tot, and none is ever freed. Measured in C++ at N = 2*10^5, U = 10^9: 124 MB to start, then about 500 nodes (10 KB) an update, so 10^4 updates add 100 MB

from bisect import bisect_left


# tree = Tree(edges, root, vals, valLo, valHi)
#
# edges: the tree's n - 1 edges. Whether nodes are 0..n-1 or 1..n is detected automatically from the edge list
#        (smallest label is 0 -> 0..n-1, otherwise 1..n; with no edges, from root)
#   [(a, b), ...]        e.g. [(0, 1), (1, 2)]
#   [(a, b, w), ...]     also accepted: the weights are ignored here
# root: the root node (required), e.g. 0 or 1.
# vals: the node values, vals[node] is node's value
#   nodes 0..n-1: length n        e.g. n = 3: [10, 20, 30]         node 0 -> 10
#   nodes 1..n:   length n + 1    e.g. n = 3: [0, 10, 20, 30]      vals[0] is ignored, node 1 -> 10
# valLo: every value ever held is >= valLo (any integer, negative is fine).
# valHi: every value ever held is <= valHi.
#
#   Tree([(0, 1), (1, 2)], 0, [10, 20, 30], valLo, valHi)       # nodes 0..2, rooted at 0
#   Tree([(1, 2), (2, 3)], 1, [0, 10, 20, 30], valLo, valHi)    # nodes 1..3, rooted at 1
#
# Nodes go in and come out with your labels, and -1 means "no such node". A label that is not in the tree raises
# IndexError. A path a..b includes both a and b. Nothing recurses, so a 10^6-node chain is fine.
#
# How it works: every node keeps a version of a persistent segment tree over the value range [valLo, valHi], holding the
# starting values on its path from the root. A version copies its parent's and adds one value. Changes go into a Fenwick
# tree over the heavy-light positions, each of its nodes a tree over the value range too: changing the value at v from
# old to new counts old one time less and new one time more from pos[v] on, and the opposite from just past v's subtree
# on. So the path root..u is u's version plus the O(log n) Fenwick trees through pos[u], a path a..b is root..a +
# root..b - root..lca - root..parent(lca), and all those trees walk down the value range together: O(log n * log U) a
# query, with U = valHi - valLo + 1.
#
# Memory is the price. The versions take about n * log U tree nodes, and every update adds up to 4 * log n * log U more,
# none of them ever freed. Measured in C++ with n = 2 * 10^5 and U = 10^9: 124 MB to start, then about 500 nodes (10 KB)
# an update, so 10^4 updates add 100 MB and 10^5 would add a gigabyte. A tighter [valLo, valHi] makes both smaller. With
# no updates at all, the path-rank templates (fixed values) are lighter and a log faster.
class Tree:
    # O(n log U) -- builds the layout and a version per node; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, vals has the wrong length, or a value is outside [valLo, valHi]
    def __init__(self, edges, root, vals, valLo, valHi):
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
        val = list(vals)

        # lc, rc, cnt, tot: one pool of tree nodes over the value range (a value's place in it is value - valLo): a
        # node's two children, how many values it holds and their sum; node 0 is the empty tree. ver[v] is the root of
        # v's version: its parent's, plus its own value (the versions share everything else).
        span = valHi - valLo + 1
        depth = max(1, (span - 1).bit_length())
        room = n * (depth + 1) + 1
        lc, rc, cnt, tot = [0] * room, [0] * room, [0] * room, [0] * room
        ver = [0] * (hi + 1)
        used = 1
        for v in bfs:
            prev = ver[par[v]] if v != root else 0
            x = val[v]
            if not valLo <= x <= valHi:
                raise ValueError(f"Tree: every value must lie in [valLo, valHi] = [{valLo}, {valHi}], got {x}")
            i = x - valLo
            cur = ver[v] = used
            a, b = 0, span - 1
            while True:
                cnt[cur] = cnt[prev] + 1
                tot[cur] = tot[prev] + x
                used += 1
                if a == b:
                    break
                mid = (a + b) >> 1
                if i <= mid:
                    rc[cur] = rc[prev]
                    lc[cur] = used
                    prev = lc[prev]
                    b = mid
                else:
                    lc[cur] = lc[prev]
                    rc[cur] = used
                    prev = rc[prev]
                    a = mid + 1
                cur = used
        del lc[used:], rc[used:], cnt[used:], tot[used:]  # (an update appends the nodes it needs)
        self.lc, self.rc, self.cnt, self.tot, self.ver, self.val = lc, rc, cnt, tot, ver, val
        self.top = [0] * (n + 1)  # the Fenwick tree over the positions: top[i] is its i-th tree of changes (0: empty)
        self.valLo, self.valHi, self.span = valLo, valHi, span

    # a new, empty tree node at the end of the pool
    def _node(self):
        self.lc.append(0)
        self.rc.append(0)
        self.cnt.append(0)
        self.tot.append(0)
        return len(self.cnt) - 1

    # from position p on, the Fenwick trees count x d more times (d is 1 or -1); nothing when p is past the last
    # position
    def _change(self, p, x, d):
        lc, rc, cnt, tot, top = self.lc, self.rc, self.cnt, self.tot, self.top
        place, last, n = x - self.valLo, self.span - 1, self.n
        i = p + 1
        while i <= n:
            if not top[i]:
                top[i] = self._node()
            cur = top[i]
            a, b = 0, last
            while True:
                cnt[cur] += d
                tot[cur] += d * x
                if a == b:
                    break
                mid = (a + b) >> 1
                if place <= mid:
                    if not lc[cur]:
                        lc[cur] = self._node()
                    cur = lc[cur]
                    b = mid
                else:
                    if not rc[cur]:
                        rc[cur] = self._node()
                    cur = rc[cur]
                    a = mid + 1
            i += i & -i

    # the value kept at node v becomes x: every path root..u with u in v's subtree loses the old value and gains x
    def _set(self, v, x):
        old = self.val[v]
        if x == old:
            return
        if not self.valLo <= x <= self.valHi:
            raise ValueError(f"Tree: every value must lie in [valLo, valHi] = [{self.valLo}, {self.valHi}], got {x}")
        p = self.pos[v]
        q = p + self.sz[v]
        self._change(p, old, -1)
        self._change(p, x, 1)
        self._change(q, old, 1)
        self._change(q, x, -1)
        self.val[v] = x

    # how many values of the range [valLo, valHi] are < x (after: <= x): the rank x would take
    def _rankOf(self, x, after):
        if x < self.valLo:
            return 0
        if x > self.valHi:
            return self.span
        return x - self.valLo + (1 if after else 0)

    # adds to `trees` the ones that together hold the path root..v: v's version and the Fenwick trees through pos[v]
    def _gather(self, v, trees):
        top = self.top
        trees.append(self.ver[v])
        i = self.pos[v] + 1
        while i > 0:
            if top[i]:
                trees.append(top[i])
            i -= i & -i

    # the trees whose counts add up to the path a..b: (the ones that count for it, the ones that count against it)
    def _roots(self, a, b):
        c = self._lca(a, b)
        plus, minus = [], []
        self._gather(a, plus)
        self._gather(b, plus)
        self._gather(c, minus)
        if c != self.root:
            self._gather(self.par[c], minus)
        return plus, minus

    # how many values a path has, and their sum
    def _countOf(self, rs):
        cnt = self.cnt
        return sum(cnt[t] for t in rs[0]) - sum(cnt[t] for t in rs[1])

    def _sumOf(self, rs):
        tot = self.tot
        return sum(tot[t] for t in rs[0]) - sum(tot[t] for t in rs[1])

    # the kth smallest value of a path (1 <= k <= its size): its trees walk down the value range together
    def _kthValue(self, rs, k):
        lc, rc, cnt = self.lc, self.rc, self.cnt
        plus, minus = rs
        lo, hi = 0, self.span - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
            if k <= left:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
            else:
                k -= left
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
        return self.valLo + lo

    # (how many, their sum) of a path's values that are among the r smallest values of the range [valLo, valHi]
    def _valuesBelow(self, rs, r):
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        plus, minus = rs
        lo, hi = 0, self.span - 1
        if r <= 0:
            return 0, 0
        if r > hi:
            return self._countOf(rs), self._sumOf(rs)
        many = total = 0
        while lo < hi:
            mid = (lo + hi) >> 1
            if r > mid:  # the whole left half is wanted
                many += sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
                total += sum(tot[lc[t]] for t in plus) - sum(tot[lc[t]] for t in minus)
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
            else:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
        return many, total

    # the sum of a path's k smallest values (0 <= k <= its size)
    def _smallestSum(self, rs, k):
        if k <= 0:
            return 0
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        plus, minus = rs
        total = 0
        lo, hi = 0, self.span - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = sum(cnt[lc[t]] for t in plus) - sum(cnt[lc[t]] for t in minus)
            if k <= left:
                plus, minus = [lc[t] for t in plus], [lc[t] for t in minus]
                hi = mid
            else:
                k -= left
                total += sum(tot[lc[t]] for t in plus) - sum(tot[lc[t]] for t in minus)
                plus, minus = [rc[t] for t in plus], [rc[t] for t in minus]
                lo = mid + 1
        return total + k * (self.valLo + lo)

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.val[node]

    # O(log n * log U) -- val(node) = x; the new value must lie in [valLo, valHi]
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self._set(node, x)

    # O(log n * log U) -- val(node) += x; the new value must lie in [valLo, valHi]
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self._set(node, self.val[node] + x)

    # O(log n * log U) -- val(node) = max(val, x); the new value must lie in [valLo, valHi]
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        if x > self.val[node]:
            self._set(node, x)

    # O(log n * log U) -- val(node) = min(val, x); the new value must lie in [valLo, valHi]
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        if x < self.val[node]:
            self._set(node, x)

    # O(log n * log U) -- kth smallest of the node values on the path a..b (1-indexed: k = 1 is the min); needs 1 <= k
    # <= the path's size, else IndexError
    def nodePathKthSmallest(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathKthSmallest", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 1 <= k <= size:
            raise IndexError(f"nodePathKthSmallest: needs 1 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._kthValue(rs, k)

    # O(log n * log U) -- kth largest of the node values on the path a..b (1-indexed: k = 1 is the max); needs 1 <= k <=
    # the path's size, else IndexError
    def nodePathKthLargest(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathKthLargest", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 1 <= k <= size:
            raise IndexError(f"nodePathKthLargest: needs 1 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._kthValue(rs, size + 1 - k)

    # O(log n * log U) -- sum of the k smallest node values on the path a..b; needs 0 <= k <= the path's size, else
    # IndexError
    def nodePathSumSmallestK(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumSmallestK", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 0 <= k <= size:
            raise IndexError(f"nodePathSumSmallestK: needs 0 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._smallestSum(rs, k)

    # O(log n * log U) -- sum of the k largest node values on the path a..b; needs 0 <= k <= the path's size, else
    # IndexError
    def nodePathSumLargestK(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumLargestK", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 0 <= k <= size:
            raise IndexError(f"nodePathSumLargestK: needs 0 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._sumOf(rs) - self._smallestSum(rs, size - k)

    # O(log n * log U) -- sum of the kFrom-th ... kTo-th smallest node values on the path a..b (1-indexed); needs 1 <=
    # kFrom <= kTo <= the path's size, else IndexError
    def nodePathSumKthSmallestRange(self, a, b, kFrom, kTo):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumKthSmallestRange", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 1 <= kFrom <= kTo <= size:
            raise IndexError(f"nodePathSumKthSmallestRange: needs 1 <= kFrom <= kTo <= {size} (the path's size), "
                             f"got kFrom = {kFrom}, kTo = {kTo}")
        return self._smallestSum(rs, kTo) - self._smallestSum(rs, kFrom - 1)

    # O(log n * log U) -- sum of the kFrom-th ... kTo-th largest node values on the path a..b (1-indexed); needs 1 <=
    # kFrom <= kTo <= the path's size, else IndexError
    def nodePathSumKthLargestRange(self, a, b, kFrom, kTo):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumKthLargestRange", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        if not 1 <= kFrom <= kTo <= size:
            raise IndexError(f"nodePathSumKthLargestRange: needs 1 <= kFrom <= kTo <= {size} (the path's size), "
                             f"got kFrom = {kFrom}, kTo = {kTo}")
        return self._smallestSum(rs, size - kFrom + 1) - self._smallestSum(rs, size - kTo)

    # O(log n * log U) -- sum of the node values on the path a..b
    def nodePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSum", a, b)
        rs = self._roots(a, b)
        return self._sumOf(rs)

    # O(log n * log U) -- min node value on the path a..b
    def nodePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMin", a, b)
        rs = self._roots(a, b)
        return self._kthValue(rs, 1)

    # O(log n * log U) -- max node value on the path a..b
    def nodePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathMax", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        return self._kthValue(rs, size)

    # O(log n * log U) -- how many node values on the path a..b are < x
    def nodePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLtX", a, b)
        rs = self._roots(a, b)
        return self._valuesBelow(rs, self._rankOf(x, False))[0]

    # O(log n * log U) -- sum of the node values on the path a..b that are < x
    def nodePathSumLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumLtX", a, b)
        rs = self._roots(a, b)
        return self._valuesBelow(rs, self._rankOf(x, False))[1]

    # O(log n * log U) -- how many node values on the path a..b are <= x
    def nodePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountLteX", a, b)
        rs = self._roots(a, b)
        return self._valuesBelow(rs, self._rankOf(x, True))[0]

    # O(log n * log U) -- sum of the node values on the path a..b that are <= x
    def nodePathSumLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumLteX", a, b)
        rs = self._roots(a, b)
        return self._valuesBelow(rs, self._rankOf(x, True))[1]

    # O(log n * log U) -- how many node values on the path a..b are > x
    def nodePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGtX", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        return size - self._valuesBelow(rs, self._rankOf(x, True))[0]

    # O(log n * log U) -- sum of the node values on the path a..b that are > x
    def nodePathSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumGtX", a, b)
        rs = self._roots(a, b)
        return self._sumOf(rs) - self._valuesBelow(rs, self._rankOf(x, True))[1]

    # O(log n * log U) -- how many node values on the path a..b are >= x
    def nodePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountGteX", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        return size - self._valuesBelow(rs, self._rankOf(x, False))[0]

    # O(log n * log U) -- sum of the node values on the path a..b that are >= x
    def nodePathSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumGteX", a, b)
        rs = self._roots(a, b)
        return self._sumOf(rs) - self._valuesBelow(rs, self._rankOf(x, False))[1]

    # O(log n * log U) -- how many node values on the path a..b are in [low, high]
    def nodePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountInValRange", a, b)
        rs = self._roots(a, b)
        if low > high:
            return 0
        upTo = self._valuesBelow(rs, self._rankOf(high, True))[0]
        return upTo - self._valuesBelow(rs, self._rankOf(low, False))[0]

    # O(log n * log U) -- sum of the node values on the path a..b in [low, high]
    def nodePathSumInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumInValRange", a, b)
        rs = self._roots(a, b)
        if low > high:
            return 0
        upTo = self._valuesBelow(rs, self._rankOf(high, True))[1]
        return upTo - self._valuesBelow(rs, self._rankOf(low, False))[1]

    # O(log n * log U) -- how many node values on the path a..b equal x
    def nodePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountOccurrences", a, b)
        rs = self._roots(a, b)
        upTo = self._valuesBelow(rs, self._rankOf(x, True))[0]
        return upTo - self._valuesBelow(rs, self._rankOf(x, False))[0]

    # O(log n * log U) -- sum of |val - x| over the node values on the path a..b
    def nodePathSumAbsDiffToX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumAbsDiffToX", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        many, low = self._valuesBelow(rs, self._rankOf(x, False))
        return x * many - low + (self._sumOf(rs) - low) - x * (size - many)

    # O(log n * log U) -- sum of |val - median| over the node values on the path a..b (the lower median)
    def nodePathSumAbsDiffToMedian(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSumAbsDiffToMedian", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        x = self._kthValue(rs, (size + 1) // 2)
        many, low = self._valuesBelow(rs, self._rankOf(x, False))
        return x * many - low + (self._sumOf(rs) - low) - x * (size - many)

    # O(log n * log U) -- smallest of the node values on the path a..b that is >= x (None if none)
    def nodePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGteX", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        k = self._valuesBelow(rs, self._rankOf(x, False))[0]
        return None if k == size else self._kthValue(rs, k + 1)

    # O(log n * log U) -- smallest of the node values on the path a..b that is > x (None if none)
    def nodePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathSmallestGtX", a, b)
        rs = self._roots(a, b)
        size = self._countOf(rs)
        k = self._valuesBelow(rs, self._rankOf(x, True))[0]
        return None if k == size else self._kthValue(rs, k + 1)

    # O(log n * log U) -- largest of the node values on the path a..b that is <= x (None if none)
    def nodePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLteX", a, b)
        rs = self._roots(a, b)
        k = self._valuesBelow(rs, self._rankOf(x, True))[0]
        return None if k == 0 else self._kthValue(rs, k)

    # O(log n * log U) -- largest of the node values on the path a..b that is < x (None if none)
    def nodePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLargestLtX", a, b)
        rs = self._roots(a, b)
        k = self._valuesBelow(rs, self._rankOf(x, False))[0]
        return None if k == 0 else self._kthValue(rs, k)

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
