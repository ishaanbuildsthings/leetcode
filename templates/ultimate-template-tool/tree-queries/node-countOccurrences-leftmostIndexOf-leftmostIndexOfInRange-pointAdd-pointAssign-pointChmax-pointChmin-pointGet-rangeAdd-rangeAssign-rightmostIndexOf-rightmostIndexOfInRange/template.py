# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/node-countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rightmostIndexOf-rightmostIndexOfInRange/template.py
# @operations: countAtDepthInSubtree depth isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAdd nodeAssign nodeChmax nodeChmin nodeGet nodeNearestAncestorEqX nodePathAdd nodePathAssign nodePathCountOccurrences nodePathFirstEqX nodePathLastEqX nodeSubtreeAdd nodeSubtreeAssign nodeSubtreeCountOccurrences parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
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
#   nodeAdd: sqrt(N)
#   nodeAssign: sqrt(N)
#   nodeChmax: sqrt(N)
#   nodeChmin: sqrt(N)
#   nodeGet: 1
#   nodeNearestAncestorEqX: sqrt(N)*log(N)
#   nodePathAdd: sqrt(N)*log(N)
#   nodePathAssign: sqrt(N)*log(N)
#   nodePathCountOccurrences: sqrt(N)*log(N)
#   nodePathFirstEqX: sqrt(N)*log(N)
#   nodePathLastEqX: sqrt(N)*log(N)
#   nodeSubtreeAdd: sqrt(N)
#   nodeSubtreeAssign: sqrt(N)
#   nodeSubtreeCountOccurrences: sqrt(N)
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
#   node: vals[1*N] cnt[1*N]
#   tags: add[1*sqrt(N)] asg[1*sqrt(N)]
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: sqrt(N) blocks; cnt[b] counts the block's stored values, and the block tag (assign, then add) is applied on read

from math import isqrt
from random import getrandbits

# "How many times does x appear in a[l..r]?" and "where is x's first / last copy (in a[l..r])?", with range add, range
# assign and point updates. 0-based, inclusive.
# Sqrt decomposition: each block keeps its stored values, a value -> count table of them, and one pending tag "value =
# (asg if assigned else stored) + add". A whole block answers a count from its table in O(1): look up x - add (or
# compare x to asg + add when the block is assigned). A partial block bakes its tag in, edits the few slots it covers,
# and patches its table one slot at a time. A first / last search skips every block whose table lacks x and scans only
# the first block that has it.


class SqrtOccurrences:
    __slots__ = ("n", "B", "vals", "cnt", "add", "asg", "salt")

    # O(N)
    def __init__(self, arr):
        n = self.n = len(arr)
        B = self.B = max(1, isqrt(n))
        nb = (n + B - 1) // B
        self.vals = list(arr)
        self.cnt = [{} for _ in range(nb)]
        # cnt's keys are values salted with this, so no fixed input can make them collide
        salt = self.salt = getrandbits(62)
        for i, v in enumerate(arr):
            c = self.cnt[i // B]
            v ^= salt
            c[v] = c.get(v, 0) + 1
        self.add = [0] * nb
        self.asg = [None] * nb  # None = not assigned

    def _range(self, b):
        return b * self.B, min(self.n, (b + 1) * self.B) - 1

    # O(sqrt N) -- bake block b's tag into its stored values and clear it
    def _push(self, b):
        add, asg = self.add[b], self.asg[b]
        if not add and asg is None:
            return
        lo, hi = self._range(b)
        vals = self.vals
        if asg is not None:
            v = asg + add
            for i in range(lo, hi + 1):
                vals[i] = v
            self.cnt[b] = {v ^ self.salt: hi - lo + 1}
        else:
            for i in range(lo, hi + 1):
                vals[i] += add
            salt = self.salt
            self.cnt[b] = {((k ^ salt) + add) ^ salt: c for k, c in self.cnt[b].items()}
        self.add[b] = 0
        self.asg[b] = None

    # O(1) -- a[i] = v inside an untagged block, keeping its table in sync
    def _set(self, b, i, v):
        c, salt = self.cnt[b], self.salt
        old = self.vals[i] ^ salt
        if c[old] == 1:
            del c[old]
        else:
            c[old] -= 1
        self.vals[i] = v
        v ^= salt
        c[v] = c.get(v, 0) + 1

    # whole blocks get a tag; the partial ends are pushed and edited slot by slot
    def _apply(self, l, r, tag, edit):
        B = self.B
        for b in range(l // B, r // B + 1):
            lo, hi = self._range(b)
            if l <= lo and hi <= r:
                tag(b)
            else:
                self._push(b)
                for i in range(max(l, lo), min(r, hi) + 1):
                    self._set(b, i, edit(self.vals[i]))

    # O(sqrt N) -- a[i] += x for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAdd(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAdd: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return

        def tag(b):
            self.add[b] += x
        self._apply(l, r, tag, lambda v: v + x)

    # O(sqrt N) -- a[i] = x for i in [l, r]; needs 0 <= l <= r < n, else IndexError
    def rangeAssign(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return

        def tag(b):
            self.asg[b] = x
            self.add[b] = 0
        self._apply(l, r, tag, lambda v: x)

    # O(sqrt N) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < n, else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        if l > r:
            return 0
        B, res, salt = self.B, 0, self.salt
        for b in range(l // B, r // B + 1):
            lo, hi = self._range(b)
            add, asg = self.add[b], self.asg[b]
            if l <= lo and hi <= r:
                if asg is not None:
                    res += hi - lo + 1 if asg + add == x else 0
                else:
                    res += self.cnt[b].get((x - add) ^ salt, 0)
            else:
                vals = self.vals
                for i in range(max(l, lo), min(r, hi) + 1):
                    if (asg if asg is not None else vals[i]) + add == x:
                        res += 1
        return res

    # O(sqrt N) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._search(0, self.n - 1, x, False)

    # O(sqrt N) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._search(0, self.n - 1, x, True)

    # O(sqrt N) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._search(l, r, x, False)

    # O(sqrt N) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < n, else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.n:
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < n, got l = {l}, r = {r}, n = {self.n}")
        return self._search(l, r, x, True)

    # the first (rev: last) i in [l, r] with a[i] == x, or -1
    def _search(self, l, r, x, rev):
        if l > r:
            return -1
        B, vals, salt = self.B, self.vals, self.salt
        blocks = range(l // B, r // B + 1)
        for b in reversed(blocks) if rev else blocks:
            lo, hi = self._range(b)
            lo, hi = max(l, lo), min(r, hi)
            add, asg = self.add[b], self.asg[b]
            if asg is not None:
                if asg + add == x:
                    return hi if rev else lo
                continue
            want = x - add
            if want ^ salt not in self.cnt[b]:  # (a partial block too: x isn't anywhere in it)
                continue
            for i in range(hi, lo - 1, -1) if rev else range(lo, hi + 1):
                if vals[i] == want:
                    return i
        return -1

    # O(1) -- a[i]; needs 0 <= i < n, else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.n:
            raise IndexError(f"pointGet: needs 0 <= i < n, got i = {i}, n = {self.n}")
        b = i // self.B
        asg = self.asg[b]
        return (asg if asg is not None else self.vals[i]) + self.add[b]

    # O(N) -- the whole array (each a[i] is O(1))
    def getAll(self):
        return [self.pointGet(i) for i in range(self.n)]

    # O(sqrt N) -- a[i] = val; needs 0 <= i < n, else IndexError
    def pointAssign(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAssign: needs 0 <= i < n, got i = {i}, n = {self.n}")
        b = i // self.B
        self._push(b)
        self._set(b, i, val)

    # O(sqrt N) -- a[i] += delta; needs 0 <= i < n, else IndexError
    def pointAdd(self, i, delta):
        if not 0 <= i < self.n:
            raise IndexError(f"pointAdd: needs 0 <= i < n, got i = {i}, n = {self.n}")
        self.pointAssign(i, self.pointGet(i) + delta)

    # O(sqrt N) -- a[i] = max(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmax(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmax: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val > self.pointGet(i):
            self.pointAssign(i, val)

    # O(sqrt N) -- a[i] = min(a[i], val); needs 0 <= i < n, else IndexError
    def pointChmin(self, i, val):
        if not 0 <= i < self.n:
            raise IndexError(f"pointChmin: needs 0 <= i < n, got i = {i}, n = {self.n}")
        if val < self.pointGet(i):
            self.pointAssign(i, val)


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
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). The values sit in the range structure above
# (SqrtOccurrences) in position order: a subtree is one range of it, and a path a..b is O(log n) ranges, one per chain
# it crosses.
class Tree:
    # O(n) -- builds the layout and the range structure; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, or vals has the wrong length
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
        self.seg = SqrtOccurrences([vals[v] for v in order])  # the values, in position order

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.seg.pointGet(self.pos[node])

    # O(sqrt(n)) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.seg.pointAssign(self.pos[node], x)

    # O(sqrt(n)) -- val(node) += x
    def nodeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAdd", node)
        self.seg.pointAdd(self.pos[node], x)

    # O(sqrt(n)) -- val(node) = max(val, x)
    def nodeChmax(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmax", node)
        self.seg.pointChmax(self.pos[node], x)

    # O(sqrt(n)) -- val(node) = min(val, x)
    def nodeChmin(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeChmin", node)
        self.seg.pointChmin(self.pos[node], x)

    # O(sqrt(n) * log n) -- val = x for every node on the path a..b
    def nodePathAssign(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAssign", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.rangeAssign
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, x) if l <= r else apply(r, l, x)

    # O(sqrt(n) * log n) -- val += x for every node on the path a..b
    def nodePathAdd(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAdd", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.seg.rangeAdd
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        apply(l, r, x) if l <= r else apply(r, l, x)

    # O(sqrt(n) * log n) -- how many node values on the path a..b equal x
    def nodePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.seg.countOccurrences
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        res += query(l, r, x)
        return res

    # O(sqrt(n) * log n) -- nearest ancestor of node (node included) with val = x (-1 if none)
    def nodeNearestAncestorEqX(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeNearestAncestorEqX", node)
        head, par, pos, find = self.head, self.par, self.pos, self.seg.rightmostIndexOfInRange
        while node != -1:
            i = find(pos[head[node]], pos[node], x)
            if i != -1:
                return self.order[i]
            node = par[head[node]]
        return -1

    def _firstEqX(self, a, b, x):
        head, par, dep, pos, order = self.head, self.par, self.dep, self.pos, self.order
        first, last = self.seg.leftmostIndexOfInRange, self.seg.rightmostIndexOfInRange
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

    # O(sqrt(n) * log n) -- first node walking a -> b with val = x (-1 if none)
    def nodePathFirstEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstEqX", a, b)
        return self._firstEqX(a, b, x)

    # O(sqrt(n) * log n) -- last node walking a -> b with val = x (-1 if none)
    def nodePathLastEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastEqX", a, b)
        return self._firstEqX(b, a, x)

    # O(sqrt(n)) -- val = x for every node in node's subtree
    def nodeSubtreeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAssign", node)
        l = self.pos[node]
        self.seg.rangeAssign(l, l + self.sz[node] - 1, x)

    # O(sqrt(n)) -- val += x for every node in node's subtree
    def nodeSubtreeAdd(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAdd", node)
        l = self.pos[node]
        self.seg.rangeAdd(l, l + self.sz[node] - 1, x)

    # O(sqrt(n)) -- how many node values in node's subtree equal x
    def nodeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountOccurrences", node)
        l = self.pos[node]
        return self.seg.countOccurrences(l, l + self.sz[node] - 1, x)

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
