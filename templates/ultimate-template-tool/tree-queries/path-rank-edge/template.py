# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/path-rank-edge/template.py
# @operations: countAtDepthInSubtree depth edgeGet edgePathCountGtX edgePathCountGteX edgePathCountInValRange edgePathCountLtX edgePathCountLteX edgePathCountOccurrences edgePathKthLargest edgePathKthSmallest edgePathLargestLtX edgePathLargestLteX edgePathMax edgePathMin edgePathSmallestGtX edgePathSmallestGteX edgePathSum edgePathSumAbsDiffToMedian edgePathSumAbsDiffToX edgePathSumGtX edgePathSumGteX edgePathSumInValRange edgePathSumKthLargestRange edgePathSumKthSmallestRange edgePathSumLargestK edgePathSumLtX edgePathSumLteX edgePathSumSmallestK isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: persistent-paths
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeGet: 1
#   edgePathCountGtX: log(N)
#   edgePathCountGteX: log(N)
#   edgePathCountInValRange: log(N)
#   edgePathCountLtX: log(N)
#   edgePathCountLteX: log(N)
#   edgePathCountOccurrences: log(N)
#   edgePathKthLargest: log(N)
#   edgePathKthSmallest: log(N)
#   edgePathLargestLtX: log(N)
#   edgePathLargestLteX: log(N)
#   edgePathMax: log(N)
#   edgePathMin: log(N)
#   edgePathSmallestGtX: log(N)
#   edgePathSmallestGteX: log(N)
#   edgePathSum: log(N)
#   edgePathSumAbsDiffToMedian: log(N)
#   edgePathSumAbsDiffToX: log(N)
#   edgePathSumGtX: log(N)
#   edgePathSumGteX: log(N)
#   edgePathSumInValRange: log(N)
#   edgePathSumKthLargestRange: log(N)
#   edgePathSumKthSmallestRange: log(N)
#   edgePathSumLargestK: log(N)
#   edgePathSumLtX: log(N)
#   edgePathSumLteX: log(N)
#   edgePathSumSmallestK: log(N)
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
#   build: N*log(N)
# @memory:
#   layout: none
#   node: lc[1*N*log(N)] rc[1*N*log(N)] cnt[1*N*log(N)] tot[1*N*log(N)]
#   tags: none
#   other: ver[1*N] srt[1*N] val[1*N] par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: a version is a root in lc / rc / cnt / tot; each adds log(N) nodes to its parent's

from bisect import bisect_left, bisect_right


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
# How it works: every node keeps a version of a persistent segment tree over the values (by rank), holding the edges on
# its path from the root, each as its weight. A version copies its parent's and adds one value, so all of them take O(n
# log n) nodes. A path a..b is then ver[a] + ver[b] - 2 * ver[lca], and the versions walk down together: O(log n) a
# query. The values are fixed: there are no updates.
class Tree:
    # O(n * log n) -- builds the layout and a version per node; raises ValueError when the edges are not one tree on
    # nodes 0..n-1 or 1..n, or an edge has no weight
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
        val = [0] * (hi + 1)  # val[v]: the weight of the edge above v (the root has none)
        for e in edges:
            val[e[0] if par[e[0]] == e[1] else e[1]] = e[2]
        # one version per node: its parent's, plus the weight of the edge above it (the versions share everything else)
        srt = sorted({val[v] for v in bfs[1:]})  # the distinct values: a version is a tree over their ranks
        rank = {x: i for i, x in enumerate(srt)}
        depth = max(1, (len(srt) - 1).bit_length())
        lc = [0] * (n * (depth + 1) + 1)  # node 0 is the empty version
        rc = lc[:]
        cnt = lc[:]
        tot = lc[:]
        ver = [0] * (hi + 1)
        used = 1
        for v in bfs[1:]:
            prev = ver[par[v]]
            x = val[v]
            i = rank[x]
            cur = ver[v] = used
            a, b = 0, len(srt) - 1
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
        self.srt, self.lc, self.rc, self.cnt, self.tot, self.ver, self.val = srt, lc, rc, cnt, tot, ver, val

    # O(1) -- weight(a - b); a and b are the edge's two ends, in either order
    def edgeGet(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgeGet", a, b)
        if self.par[a] == b:
            return self.val[a]
        if self.par[b] == a:
            return self.val[b]
        raise IndexError(f"edgeGet: needs an edge between a and b, got {a} and {b}")

    # the versions whose counts add up to the edges of the path a..b: ver[a] + ver[b] - 2 * ver[lca]
    def _roots(self, a, b):
        ver = self.ver
        return ver[a], ver[b], ver[self._lca(a, b)]

    # the kth smallest value of a path (1 <= k <= its size): its versions walk down together
    def _kthValue(self, A, B, X, k):
        lc, rc, cnt = self.lc, self.rc, self.cnt
        lo, hi = 0, len(self.srt) - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]]
            if k <= left:
                A, B, X = lc[A], lc[B], lc[X]
                hi = mid
            else:
                k -= left
                A, B, X = rc[A], rc[B], rc[X]
                lo = mid + 1
        return self.srt[lo]

    # (how many, their sum) of a path's values that are among the r smallest distinct values of the tree
    def _valuesBelow(self, A, B, X, r):
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        lo, hi = 0, len(self.srt) - 1
        if r <= 0:
            return 0, 0
        if r > hi:
            return cnt[A] + cnt[B] - 2 * cnt[X], tot[A] + tot[B] - 2 * tot[X]
        many = total = 0
        while lo < hi:
            mid = (lo + hi) >> 1
            if r > mid:  # the whole left half is wanted
                many += cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]]
                total += tot[lc[A]] + tot[lc[B]] - 2 * tot[lc[X]]
                A, B, X = rc[A], rc[B], rc[X]
                lo = mid + 1
            else:
                A, B, X = lc[A], lc[B], lc[X]
                hi = mid
        return many, total

    # the sum of a path's k smallest values (0 <= k <= its size)
    def _smallestSum(self, A, B, X, k):
        if k <= 0:
            return 0
        lc, rc, cnt, tot = self.lc, self.rc, self.cnt, self.tot
        total = 0
        lo, hi = 0, len(self.srt) - 1
        while lo < hi:
            mid = (lo + hi) >> 1
            left = cnt[lc[A]] + cnt[lc[B]] - 2 * cnt[lc[X]]
            if k <= left:
                A, B, X = lc[A], lc[B], lc[X]
                hi = mid
            else:
                k -= left
                total += tot[lc[A]] + tot[lc[B]] - 2 * tot[lc[X]]
                A, B, X = rc[A], rc[B], rc[X]
                lo = mid + 1
        return total + k * self.srt[lo]

    # O(log n) -- kth smallest of the edge weights on the path a..b (1-indexed: k = 1 is the min); needs 1 <= k <= the
    # path's size, else IndexError
    def edgePathKthSmallest(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathKthSmallest", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 1 <= k <= size:
            raise IndexError(f"edgePathKthSmallest: needs 1 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._kthValue(A, B, X, k)

    # O(log n) -- kth largest of the edge weights on the path a..b (1-indexed: k = 1 is the max); needs 1 <= k <= the
    # path's size, else IndexError
    def edgePathKthLargest(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathKthLargest", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 1 <= k <= size:
            raise IndexError(f"edgePathKthLargest: needs 1 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._kthValue(A, B, X, size + 1 - k)

    # O(log n) -- sum of the k smallest edge weights on the path a..b; needs 0 <= k <= the path's size, else IndexError
    def edgePathSumSmallestK(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumSmallestK", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 0 <= k <= size:
            raise IndexError(f"edgePathSumSmallestK: needs 0 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return self._smallestSum(A, B, X, k)

    # O(log n) -- sum of the k largest edge weights on the path a..b; needs 0 <= k <= the path's size, else IndexError
    def edgePathSumLargestK(self, a, b, k):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumLargestK", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 0 <= k <= size:
            raise IndexError(f"edgePathSumLargestK: needs 0 <= k <= {size} (the path's size), "
                             f"got k = {k}")
        return tot[A] + tot[B] - 2 * tot[X] - self._smallestSum(A, B, X, size - k)

    # O(log n) -- sum of the kFrom-th ... kTo-th smallest edge weights on the path a..b (1-indexed); needs 1 <= kFrom <=
    # kTo <= the path's size, else IndexError
    def edgePathSumKthSmallestRange(self, a, b, kFrom, kTo):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumKthSmallestRange", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 1 <= kFrom <= kTo <= size:
            raise IndexError(f"edgePathSumKthSmallestRange: needs 1 <= kFrom <= kTo <= {size} (the path's size), "
                             f"got kFrom = {kFrom}, kTo = {kTo}")
        return self._smallestSum(A, B, X, kTo) - self._smallestSum(A, B, X, kFrom - 1)

    # O(log n) -- sum of the kFrom-th ... kTo-th largest edge weights on the path a..b (1-indexed); needs 1 <= kFrom <=
    # kTo <= the path's size, else IndexError
    def edgePathSumKthLargestRange(self, a, b, kFrom, kTo):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumKthLargestRange", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if not 1 <= kFrom <= kTo <= size:
            raise IndexError(f"edgePathSumKthLargestRange: needs 1 <= kFrom <= kTo <= {size} (the path's size), "
                             f"got kFrom = {kFrom}, kTo = {kTo}")
        return self._smallestSum(A, B, X, size - kFrom + 1) - self._smallestSum(A, B, X, size - kTo)

    # O(log n) -- sum of the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSum(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSum", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        return tot[A] + tot[B] - 2 * tot[X]

    # O(log n) -- min edge weight on the path a..b; inf when a == b (no edges)
    def edgePathMin(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMin", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if size == 0:
            return float("inf")
        return self._kthValue(A, B, X, 1)

    # O(log n) -- max edge weight on the path a..b; -inf when a == b (no edges)
    def edgePathMax(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathMax", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if size == 0:
            return float("-inf")
        return self._kthValue(A, B, X, size)

    # O(log n) -- how many edge weights on the path a..b are < x; 0 when a == b (no edges)
    def edgePathCountLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLtX", a, b)
        A, B, X = self._roots(a, b)
        return self._valuesBelow(A, B, X, bisect_left(self.srt, x))[0]

    # O(log n) -- sum of the edge weights on the path a..b that are < x; 0 when a == b (no edges)
    def edgePathSumLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumLtX", a, b)
        A, B, X = self._roots(a, b)
        return self._valuesBelow(A, B, X, bisect_left(self.srt, x))[1]

    # O(log n) -- how many edge weights on the path a..b are <= x; 0 when a == b (no edges)
    def edgePathCountLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountLteX", a, b)
        A, B, X = self._roots(a, b)
        return self._valuesBelow(A, B, X, bisect_right(self.srt, x))[0]

    # O(log n) -- sum of the edge weights on the path a..b that are <= x; 0 when a == b (no edges)
    def edgePathSumLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumLteX", a, b)
        A, B, X = self._roots(a, b)
        return self._valuesBelow(A, B, X, bisect_right(self.srt, x))[1]

    # O(log n) -- how many edge weights on the path a..b are > x; 0 when a == b (no edges)
    def edgePathCountGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGtX", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        return size - self._valuesBelow(A, B, X, bisect_right(self.srt, x))[0]

    # O(log n) -- sum of the edge weights on the path a..b that are > x; 0 when a == b (no edges)
    def edgePathSumGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumGtX", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        return tot[A] + tot[B] - 2 * tot[X] - self._valuesBelow(A, B, X, bisect_right(self.srt, x))[1]

    # O(log n) -- how many edge weights on the path a..b are >= x; 0 when a == b (no edges)
    def edgePathCountGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountGteX", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        return size - self._valuesBelow(A, B, X, bisect_left(self.srt, x))[0]

    # O(log n) -- sum of the edge weights on the path a..b that are >= x; 0 when a == b (no edges)
    def edgePathSumGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumGteX", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        return tot[A] + tot[B] - 2 * tot[X] - self._valuesBelow(A, B, X, bisect_left(self.srt, x))[1]

    # O(log n) -- how many edge weights on the path a..b are in [low, high]; 0 when a == b (no edges)
    def edgePathCountInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountInValRange", a, b)
        A, B, X = self._roots(a, b)
        if low > high:
            return 0
        upTo = self._valuesBelow(A, B, X, bisect_right(self.srt, high))[0]
        return upTo - self._valuesBelow(A, B, X, bisect_left(self.srt, low))[0]

    # O(log n) -- sum of the edge weights on the path a..b in [low, high]; 0 when a == b (no edges)
    def edgePathSumInValRange(self, a, b, low, high):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumInValRange", a, b)
        A, B, X = self._roots(a, b)
        if low > high:
            return 0
        upTo = self._valuesBelow(A, B, X, bisect_right(self.srt, high))[1]
        return upTo - self._valuesBelow(A, B, X, bisect_left(self.srt, low))[1]

    # O(log n) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    def edgePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountOccurrences", a, b)
        A, B, X = self._roots(a, b)
        upTo = self._valuesBelow(A, B, X, bisect_right(self.srt, x))[0]
        return upTo - self._valuesBelow(A, B, X, bisect_left(self.srt, x))[0]

    # O(log n) -- sum of |weight - x| over the edge weights on the path a..b; 0 when a == b (no edges)
    def edgePathSumAbsDiffToX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumAbsDiffToX", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        many, low = self._valuesBelow(A, B, X, bisect_left(self.srt, x))
        return x * many - low + (tot[A] + tot[B] - 2 * tot[X] - low) - x * (size - many)

    # O(log n) -- sum of |weight - median| over the edge weights on the path a..b (the lower median); needs at least one
    # edge (a != b), else IndexError
    def edgePathSumAbsDiffToMedian(self, a, b):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSumAbsDiffToMedian", a, b)
        A, B, X = self._roots(a, b)
        cnt, tot = self.cnt, self.tot
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        if size == 0:
            raise IndexError("edgePathSumAbsDiffToMedian: needs at least one edge (a != b)")
        x = self._kthValue(A, B, X, (size + 1) // 2)
        many, low = self._valuesBelow(A, B, X, bisect_left(self.srt, x))
        return x * many - low + (tot[A] + tot[B] - 2 * tot[X] - low) - x * (size - many)

    # O(log n) -- smallest of the edge weights on the path a..b that is >= x (None if none)
    def edgePathSmallestGteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGteX", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        k = self._valuesBelow(A, B, X, bisect_left(self.srt, x))[0]
        return None if k == size else self._kthValue(A, B, X, k + 1)

    # O(log n) -- smallest of the edge weights on the path a..b that is > x (None if none)
    def edgePathSmallestGtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathSmallestGtX", a, b)
        A, B, X = self._roots(a, b)
        cnt = self.cnt
        size = cnt[A] + cnt[B] - 2 * cnt[X]
        k = self._valuesBelow(A, B, X, bisect_right(self.srt, x))[0]
        return None if k == size else self._kthValue(A, B, X, k + 1)

    # O(log n) -- largest of the edge weights on the path a..b that is <= x (None if none)
    def edgePathLargestLteX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLteX", a, b)
        A, B, X = self._roots(a, b)
        k = self._valuesBelow(A, B, X, bisect_right(self.srt, x))[0]
        return None if k == 0 else self._kthValue(A, B, X, k)

    # O(log n) -- largest of the edge weights on the path a..b that is < x (None if none)
    def edgePathLargestLtX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLargestLtX", a, b)
        A, B, X = self._roots(a, b)
        k = self._valuesBelow(A, B, X, bisect_left(self.srt, x))[0]
        return None if k == 0 else self._kthValue(A, B, X, k)

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
