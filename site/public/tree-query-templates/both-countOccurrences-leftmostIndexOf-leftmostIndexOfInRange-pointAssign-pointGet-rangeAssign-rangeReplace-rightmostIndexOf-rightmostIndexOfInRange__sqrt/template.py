# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/tree-queries/both-countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/template.py
# The range structure inside is https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/countOccurrences-leftmostIndexOf-leftmostIndexOfInRange-pointAssign-pointGet-rangeAssign-rangeReplace-rightmostIndexOf-rightmostIndexOfInRange__sqrt/template.py
# @operations: countAtDepthInSubtree depth edgeAssign edgeGet edgeNearestAncestorEqX edgePathAssign edgePathCountOccurrences edgePathFirstEqX edgePathLastEqX edgeSubtreeAssign edgeSubtreeCountOccurrences isAncestor isOnPath kthAncestor kthNodeOnPath lca lcaRootedAt median nextNodeOnPath nodeAssign nodeGet nodeNearestAncestorEqX nodePathAssign nodePathCountOccurrences nodePathFirstEqX nodePathLastEqX nodeSubtreeAssign nodeSubtreeCountOccurrences parent parentRootedAt pathIntersection pathNodes subtreeSize subtreeSizeRootedAt unweightedDist unweightedDistBetweenPaths unweightedDistToPath
# @data-structure-type: sqrt
# @complexities:
#   countAtDepthInSubtree: log(N)
#   depth: 1
#   edgeAssign: 1 amortized
#   edgeGet: 1 amortized
#   edgeNearestAncestorEqX: sqrt(N)*log(N)
#   edgePathAssign: sqrt(N)*log(N) amortized
#   edgePathCountOccurrences: sqrt(N)*log(N)
#   edgePathFirstEqX: sqrt(N)*log(N)
#   edgePathLastEqX: sqrt(N)*log(N)
#   edgeSubtreeAssign: sqrt(N) amortized
#   edgeSubtreeCountOccurrences: sqrt(N)
#   isAncestor: 1
#   isOnPath: log(N)
#   kthAncestor: log(N)
#   kthNodeOnPath: log(N)
#   lca: log(N)
#   lcaRootedAt: log(N)
#   median: log(N)
#   nextNodeOnPath: log(N)
#   nodeAssign: 1 amortized
#   nodeGet: 1 amortized
#   nodeNearestAncestorEqX: sqrt(N)*log(N)
#   nodePathAssign: sqrt(N)*log(N) amortized
#   nodePathCountOccurrences: sqrt(N)*log(N)
#   nodePathFirstEqX: sqrt(N)*log(N)
#   nodePathLastEqX: sqrt(N)*log(N)
#   nodeSubtreeAssign: sqrt(N) amortized
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
#   node: cls[2*N] par[4*N] val[4*N] cnt[4*N] where[2*N]
#   tags: none
#   other: par[1*N] dep[1*N] sz[1*N] head[1*N] pos[1*N] order[1*N] depthPos[1*N] depthStart[1*N]
#   note: blocks of about sqrt(N) values; each block's values are classes joined by a union-find (union by size, path halving: O(alpha), counted as O(1)); where maps each value in the block to its class; values are hashed, so any values work

from math import isqrt
from random import getrandbits

# Blocks whose values form a union-find of classes (mass change, CF 911G, in O(sqrt N)): the array is cut into blocks
# of about sqrt(N) values. Inside a block equal values form a class, and the classes are joined by a union-find:
# rangeReplace(l, r, x, y) on a whole block renames x's class to y, or joins it into y's, in O(1); rangeAssign joins
# every class. Only the (at most two) partly covered blocks are touched value by value. Any values work (each block
# hashes them). a[i] and a[i] = v are O(1) amortized. All indices 0-based, ranges inclusive [l, r]; searches return -1
# when nothing qualifies.
class _Block:
    # a run of the array: cls[k] is the class of its k-th value. Classes form a union-find (par);
    # a root class holds its value (val) and how many of the block's values are in it (cnt). where: value -> root class
    __slots__ = ("cls", "par", "val", "cnt", "where")
    salt = getrandbits(62)  # where's int keys are salted with this, so no fixed input can make them collide

    def __init__(self, vals):
        self.build(vals)

    def build(self, vals):  # O(len) -- the classes from scratch
        where, par, val, cnt, cls = {}, [], [], [], []
        salt = self.salt
        for v in vals:
            key = v ^ salt if type(v) is int else v
            c = where.get(key)
            if c is None:
                c = where[key] = len(par)
                par.append(c)
                val.append(v)
                cnt.append(0)
            cnt[c] += 1
            cls.append(c)
        self.cls, self.par, self.val, self.cnt, self.where = cls, par, val, cnt, where

    def __len__(self):
        return len(self.cls)

    def find(self, c):  # c's root class (path halving)
        par = self.par
        while par[c] != c:
            par[c] = par[par[c]]
            c = par[c]
        return c

    def get(self, k):  # the k-th value
        return self.val[self.find(self.cls[k])]

    def values(self):  # every value, in order
        out = [self.val[self.find(c)] for c in self.cls]
        return out

    def count(self, x):  # how many x's
        c = self.where.get(x ^ self.salt if type(x) is int else x)
        return self.cnt[c] if c is not None else 0

    def replace(self, x, y):  # O(1) -- every x becomes y: x's class is renamed, or joined to y's
        salt = self.salt
        cx = self.where.pop(x ^ salt if type(x) is int else x, None)
        if cx is None:
            return
        ky = y ^ salt if type(y) is int else y
        cy = self.where.get(ky)
        if cy is None:
            self.val[cx] = y
            self.where[ky] = cx
            return
        if self.cnt[cx] > self.cnt[cy]:  # (union by size)
            cx, cy = cy, cx
        self.par[cx] = cy
        self.cnt[cy] += self.cnt[cx]
        self.val[cy] = y
        self.where[ky] = cy

    def assignAll(self, v):
        # every value becomes v: every class joined into one (O(1) amortized: each join removes one)
        roots = list(self.where.values())
        r = max(roots, key=lambda c: self.cnt[c])
        for c in roots:
            if c != r:
                self.par[c] = r
                self.cnt[r] += self.cnt[c]
        self.val[r] = v
        self.where = {v ^ self.salt if type(v) is int else v: r}

    def assign(self, k, v):  # O(1) amortized -- the k-th value becomes v (a class of its own if v is new here)
        c = self.find(self.cls[k])
        old = self.val[c]
        if old == v:
            return
        self.cnt[c] -= 1
        salt = self.salt
        if not self.cnt[c]:
            del self.where[old ^ salt if type(old) is int else old]
        key = v ^ salt if type(v) is int else v
        d = self.where.get(key)
        if d is None:
            d = self.where[key] = len(self.par)
            self.par.append(d)
            self.val.append(v)
            self.cnt.append(0)
        self.cnt[d] += 1
        self.cls[k] = d
        if len(self.par) > 2 * len(self.cls) + 8:  # (many dead classes: start over, paid for by the assigns)
            self.build(self.values())


class SqrtReplace:
    __slots__ = ("blocks", "n", "B")

    # O(N) -- arr: the initial array (a list)
    def __init__(self, arr):
        self._fill(list(arr))

    # O(1) -- the length of the array
    def size(self):
        return self.n

    # O(N) -- the whole current array
    def getAll(self):
        out = []
        for b in self.blocks:
            out += b.values()
        return out

    # O(1) amortized) -- a[i]; needs 0 <= i < size(), else IndexError
    def pointGet(self, i):
        if not 0 <= i < self.size():
            raise IndexError(f"pointGet: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        return b.get(k)

    # O(1) amortized) -- a[i] = v; needs 0 <= i < size(), else IndexError
    def pointAssign(self, i, v):
        if not 0 <= i < self.size():
            raise IndexError(f"pointAssign: needs 0 <= i < size(), got i = {i}, n = {self.size()}")
        b, k = self._locate(i)
        b.assign(k, v)

    # O(sqrt(N)) amortized -- every a[i] == x with l <= i <= r becomes y; needs 0 <= l <= r < size(), else IndexError
    def rangeReplace(self, l, r, x, y):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeReplace: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        if x == y:
            return
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.replace(x, y)
            else:
                for k in range(lo, hi + 1):
                    if b.get(k) == x:
                        b.assign(k, y)

    # O(sqrt(N)) amortized -- a[l..r] = v; needs 0 <= l <= r < size(), else IndexError
    def rangeAssign(self, l, r, v):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rangeAssign: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        for b, lo, hi, full, _ in self._span(l, r):
            if full:
                b.assignAll(v)
            else:
                for k in range(lo, hi + 1):
                    b.assign(k, v)

    # O(sqrt(N)) -- # of i in [l, r] with a[i] == x; needs 0 <= l <= r < size(), else IndexError
    def countOccurrences(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"countOccurrences: needs 0 <= l <= r < size(), got l = {l}, r = {r}, n = {self.size()}")
        res = 0
        for b, lo, hi, full, _ in self._span(l, r):
            res += b.count(x) if full else sum(b.get(k) == x for k in range(lo, hi + 1))
        return res

    # O(sqrt(N)) -- the smallest i with a[i] == x, or -1 if x isn't in the array
    def leftmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, True)

    # O(sqrt(N)) -- the largest i with a[i] == x, or -1 if x isn't in the array
    def rightmostIndexOf(self, x):
        return self._find(0, self.n - 1, x, False)

    # O(sqrt(N)) -- the smallest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def leftmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"leftmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, True)

    # O(sqrt(N)) -- the largest i in [l, r] with a[i] == x, or -1 if there is none; needs 0 <= l <= r < size(), else
    # IndexError
    def rightmostIndexOfInRange(self, l, r, x):
        if not 0 <= l <= r < self.size():
            raise IndexError(f"rightmostIndexOfInRange: needs 0 <= l <= r < size(), got "
                             f"l = {l}, r = {r}, n = {self.size()}")
        return self._find(l, r, x, False)

    # ---- internals ----

    @staticmethod
    def _idealB(n):
        return max(1, isqrt(n))

    def _fill(self, vals):  # blocks of about _idealB values holding vals
        n = self.n = len(vals)
        B = self.B = self._idealB(n)
        self.blocks = [_Block(vals[s:s + B]) for s in range(0, n, B)]

    def _locate(self, i):  # (block, position in it) of a[i]
        return self.blocks[i // self.B], i % self.B

    def _span(self, l, r):  # (block, lo, hi, whole, start) for each block meeting a[l..r]: positions lo..hi of it,
        B = self.B  # whether that is all of it, and the index of its first value
        for j in range(l // B, r // B + 1):
            b, start = self.blocks[j], j * B
            lo, hi = max(l - start, 0), min(r - start, len(b) - 1)
            yield b, lo, hi, lo == 0 and hi == len(b) - 1, start

    def _find(self, l, r, x, left):  # the first (left) / last i in [l, r] with a[i] == x, or -1
        spans = list(self._span(l, r)) if l <= r else []
        for b, lo, hi, full, start in (spans if left else reversed(spans)):
            if full and not b.count(x):
                continue
            for k in (range(lo, hi + 1) if left else range(hi, lo - 1, -1)):
                if b.get(k) == x:
                    return start + k
        return -1


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
# stretch of positions (pos[node] .. pos[node] + sz[node] - 1). Two copies of the range structure above (SqrtReplace)
# sit over those positions: nodeSeg holds each node's value at its position, edgeSeg each edge's weight at its lower
# end's position (the root's holds no edge). A subtree is one range, and a path a..b is O(log n) ranges, one per chain
# it crosses.
class Tree:
    # O(n) -- builds the layout and the two range structures; raises ValueError when the edges are not one tree on nodes
    # 0..n-1 or 1..n, an edge has no weight, or vals has the wrong length
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
        self.nodeSeg = SqrtReplace([vals[v] for v in order])  # the node values, in position order
        self.edgeSeg = SqrtReplace(arr)  # each edge's weight, at its lower end's position

    # O(1) -- val(node)
    def nodeGet(self, node):
        if not self.lo <= node <= self.hi:
            self._bad("nodeGet", node)
        return self.nodeSeg.pointGet(self.pos[node])

    # O(1) -- val(node) = x
    def nodeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeAssign", node)
        self.nodeSeg.pointAssign(self.pos[node], x)

    # O(sqrt(n) * log n) -- val = x for every node on the path a..b
    def nodePathAssign(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathAssign", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.nodeSeg.rangeAssign
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
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.nodeSeg.countOccurrences
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

    # O(sqrt(n) * log n) -- first node walking a -> b with val = x (-1 if none)
    def nodePathFirstEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathFirstEqX", a, b)
        return self._nodeFirstEqX(a, b, x)

    # O(sqrt(n) * log n) -- last node walking a -> b with val = x (-1 if none)
    def nodePathLastEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("nodePathLastEqX", a, b)
        return self._nodeFirstEqX(b, a, x)

    # O(sqrt(n)) -- val = x for every node in node's subtree
    def nodeSubtreeAssign(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeAssign", node)
        l = self.pos[node]
        self.nodeSeg.rangeAssign(l, l + self.sz[node] - 1, x)

    # O(sqrt(n)) -- how many node values in node's subtree equal x
    def nodeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("nodeSubtreeCountOccurrences", node)
        l = self.pos[node]
        return self.nodeSeg.countOccurrences(l, l + self.sz[node] - 1, x)

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

    # O(1) -- weight(a - b) = w; a and b are the edge's two ends, in either order
    def edgeAssign(self, a, b, w):
        self.edgeSeg.pointAssign(self._edge("edgeAssign", a, b), w)

    # O(sqrt(n) * log n) -- weight = w for every edge on the path a..b
    def edgePathAssign(self, a, b, w):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathAssign", a, b)
        head, par, dep, pos, apply = self.head, self.par, self.dep, self.pos, self.edgeSeg.rangeAssign
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            apply(pos[head[a]], pos[a], w)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l != r:  # (the lca's own position is the edge above it)
            apply(l + 1, r, w) if l < r else apply(r + 1, l, w)

    # O(sqrt(n) * log n) -- how many edge weights on the path a..b equal x; 0 when a == b (no edges)
    def edgePathCountOccurrences(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathCountOccurrences", a, b)
        head, par, dep, pos, query = self.head, self.par, self.dep, self.pos, self.edgeSeg.countOccurrences
        res = 0
        while head[a] != head[b]:
            if dep[head[a]] < dep[head[b]]:
                a, b = b, a
            res += query(pos[head[a]], pos[a], x)
            a = par[head[a]]
        l, r = pos[a], pos[b]
        if l > r:
            l, r = r, l
        if l < r:  # (the lca's own position is the edge above it)
            res += query(l + 1, r, x)
        return res

    # O(sqrt(n) * log n) -- nearest edge above node (toward the root) with weight = x, as its lower end (-1 if none)
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

    # O(sqrt(n) * log n) -- first edge walking a -> b with weight = x, as its lower end (-1 if none)
    def edgePathFirstEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathFirstEqX", a, b)
        return self._edgeFirstEqX(a, b, x)

    # O(sqrt(n) * log n) -- last edge walking a -> b with weight = x, as its lower end (-1 if none)
    def edgePathLastEqX(self, a, b, x):
        if not (self.lo <= a <= self.hi and self.lo <= b <= self.hi):
            self._bad("edgePathLastEqX", a, b)
        return self._edgeFirstEqX(b, a, x)

    # O(sqrt(n)) -- weight = w for every edge in node's subtree
    def edgeSubtreeAssign(self, node, w):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeAssign", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return
        self.edgeSeg.rangeAssign(l, r, w)

    # O(sqrt(n)) -- how many edge weights in node's subtree equal x; 0 when node is a leaf (no edges)
    def edgeSubtreeCountOccurrences(self, node, x):
        if not self.lo <= node <= self.hi:
            self._bad("edgeSubtreeCountOccurrences", node)
        l, r = self.pos[node] + 1, self.pos[node] + self.sz[node] - 1
        if l > r:  # a leaf: no edges below it
            return 0
        return self.edgeSeg.countOccurrences(l, r, x)

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
