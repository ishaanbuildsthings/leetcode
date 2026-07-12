import random
from collections import defaultdict


class _Forest:
    """One level's spanning forest, held as Euler tours in a treap.
    Tour of a k-vertex tree = k vertex nodes + 2(k-1) arc nodes = 3k-2 nodes.
    A tree edge is addressed by a "slot" in 0 .. n-2, recycled by the owner."""

    __slots__ = ("lc", "rc", "pa", "sz", "eid", "pri", "mk", "ag", "pool", "arcNode", "n")

    # node 0 is null, vertex u is node u + 1, arc nodes get allocated after that
    def __init__(self, n):
        self.n = n
        cap = n + 1
        self.lc = [0] * cap
        self.rc = [0] * cap
        self.pa = [0] * cap
        self.sz = [1] * cap
        self.eid = [-1] * cap
        self.pri = [random.getrandbits(30) for _ in range(cap)]
        self.mk = [0] * cap   # bit 0 = tree edge living at this level, bit 1 = vertex owns an incident non-tree edge at this level
        self.ag = [0] * cap
        self.sz[0] = 0
        self.pool = []
        self.arcNode = [0] * (2 * max(n - 1, 1))  # arcNode[2s], arcNode[2s+1] = the two arcs of slot s

    def pull(self, x):
        lc, rc, sz, mk, ag = self.lc, self.rc, self.sz, self.mk, self.ag
        sz[x] = 1 + sz[lc[x]] + sz[rc[x]]
        ag[x] = mk[x] | ag[lc[x]] | ag[rc[x]]

    def newNode(self, e):
        if self.pool:
            x = self.pool.pop()
            self.lc[x] = self.rc[x] = self.pa[x] = 0
            self.sz[x] = 1
            self.mk[x] = self.ag[x] = 0
            self.pri[x] = random.getrandbits(30)
            self.eid[x] = e
        else:
            x = len(self.lc)
            self.lc.append(0)
            self.rc.append(0)
            self.pa.append(0)
            self.sz.append(1)
            self.eid.append(e)
            self.pri.append(random.getrandbits(30))
            self.mk.append(0)
            self.ag.append(0)
        return x

    def merge(self, a, b):
        if not a or not b:
            r = a or b
            if r:
                self.pa[r] = 0
            return r
        if self.pri[a] > self.pri[b]:
            self.rc[a] = self.merge(self.rc[a], b)
            if self.rc[a]:
                self.pa[self.rc[a]] = a
            self.pull(a)
            self.pa[a] = 0
            return a
        self.lc[b] = self.merge(a, self.lc[b])
        if self.lc[b]:
            self.pa[self.lc[b]] = b
        self.pull(b)
        self.pa[b] = 0
        return b

    # first k nodes of t go to a, the rest to b
    def split(self, t, k):
        if not t:
            return 0, 0
        self.pa[t] = 0
        if self.sz[self.lc[t]] >= k:
            a, self.lc[t] = self.split(self.lc[t], k)
            if self.lc[t]:
                self.pa[self.lc[t]] = t
            if a:
                self.pa[a] = 0
            self.pull(t)
            return a, t
        self.rc[t], b = self.split(self.rc[t], k - self.sz[self.lc[t]] - 1)
        if self.rc[t]:
            self.pa[self.rc[t]] = t
        if b:
            self.pa[b] = 0
        self.pull(t)
        return t, b

    def findRoot(self, x):
        pa = self.pa
        while pa[x]:
            x = pa[x]
        return x

    def pos(self, x):
        lc, rc, pa, sz = self.lc, self.rc, self.pa, self.sz
        k = sz[lc[x]]
        while pa[x]:
            p = pa[x]
            if rc[p] == x:
                k += sz[lc[p]] + 1
            x = p
        return k

    def updatePath(self, x):
        while x:
            self.pull(x)
            x = self.pa[x]

    def rootOf(self, u):
        return self.findRoot(u + 1)

    def sameTree(self, u, v):
        return u == v or self.rootOf(u) == self.rootOf(v)

    def treeSize(self, u):
        return (self.sz[self.rootOf(u)] + 2) // 3

    # rotate the tour so u comes first; the tour is circular, so this is free
    def reroot(self, u):
        x = u + 1
        r = self.findRoot(x)
        k = self.pos(x)
        if not k:
            return
        a, b = self.split(r, k)
        self.merge(b, a)

    def link(self, u, v, slot, e):
        self.reroot(u)
        self.reroot(v)
        ru, rv = self.rootOf(u), self.rootOf(v)
        a, b = self.newNode(e), self.newNode(e)
        self.arcNode[2 * slot] = a
        self.arcNode[2 * slot + 1] = b
        self.merge(self.merge(self.merge(ru, a), rv), b)

    def cut(self, slot):
        x, y = self.arcNode[2 * slot], self.arcNode[2 * slot + 1]
        r = self.findRoot(x)
        px, py = self.pos(x), self.pos(y)
        if px > py:
            px, py = py, px
        a, t1 = self.split(r, px)             # a = tour before the arc
        xx, t2 = self.split(t1, 1)            # xx = the arc itself
        b, t3 = self.split(t2, py - px - 1)   # b = tour of the half that breaks off
        yy, c = self.split(t3, 1)             # yy = the back arc, c = tour after it
        self.merge(a, c)
        self.pool.append(xx)
        self.pool.append(yy)

    def setVertexMark(self, u, b):
        x = u + 1
        self.mk[x] = (self.mk[x] & 1) | (2 if b else 0)
        self.updatePath(x)

    def setEdgeMark(self, slot, b):
        x = self.arcNode[2 * slot]
        self.mk[x] = (self.mk[x] & 2) | (1 if b else 0)
        self.updatePath(x)

    # O(#hits * log n): the OR aggregate lets us skip every subtree with no marked node in it
    def gather(self, t, bit, out):
        if not t or not (self.ag[t] >> bit) & 1:
            return
        self.gather(self.lc[t], bit, out)
        if (self.mk[t] >> bit) & 1:
            out.append(t)
        self.gather(self.rc[t], bit, out)


class DynamicConnectivity:
    """Fully dynamic connectivity (Holm-de Lichtenberg-Thorup, JACM 2001).
    Online edge insert + edge delete + connectivity query. Unlike DSU, deletions are allowed.
    Takes an array of vals (can be strings, tuples, etc) since it operates based on indices.
        dc = DynamicConnectivity(vals)

    Public: addEdge, removeEdge, removeEdgeBetween, areConnected, size, numComponents,
            componentId, roots, groups, sizes, elementsInGroup, and the .vals / .n fields.
    Everything else is prefixed with _ and is internal bookkeeping.

    Python constant factor is brutal; treat this as the readable reference and use the C++ one under contest limits."""

    # O(n log n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = self.n = len(vals)
        self._comps = n
        levels = 1
        while (1 << levels) < max(n, 2):
            levels += 1
        self._levels = levels = levels + 1
        self._forest = [_Forest(n) for _ in range(levels)]
        self._head = [[-1] * n for _ in range(levels)]  # head[l][u] = first arc of u's level-l non-tree list
        self._freeSlots = list(range(max(n - 1, 1) - 1, -1, -1))
        self._eu, self._ev, self._elevel, self._slot = [], [], [], []
        self._nxt, self._prv, self._seen = [], [], []
        self._freeIds = []
        self._byPair = defaultdict(list)

    def _owner(self, a):
        return self._ev[a >> 1] if a & 1 else self._eu[a >> 1]

    def _other(self, a):
        return self._eu[a >> 1] if a & 1 else self._ev[a >> 1]

    def _newId(self):
        if self._freeIds:
            return self._freeIds.pop()
        e = len(self._eu)
        self._eu.append(0)
        self._ev.append(0)
        self._elevel.append(0)
        self._slot.append(-1)
        self._seen.append(False)
        self._nxt += [-1, -1]
        self._prv += [-1, -1]
        return e

    def _addArc(self, a, l):
        u = self._owner(a)
        h = self._head[l][u]
        self._nxt[a] = h
        self._prv[a] = -1
        if h != -1:
            self._prv[h] = a
        self._head[l][u] = a
        if h == -1:
            self._forest[l].setVertexMark(u, True)

    def _delArc(self, a, l):
        u = self._owner(a)
        p, q = self._prv[a], self._nxt[a]
        if p != -1:
            self._nxt[p] = q
        else:
            self._head[l][u] = q
        if q != -1:
            self._prv[q] = p
        if self._head[l][u] == -1:
            self._forest[l].setVertexMark(u, False)

    def _makeTreeEdge(self, e, l):
        s = self._freeSlots.pop()
        self._slot[e] = s
        for i in range(l + 1):
            self._forest[i].link(self._eu[e], self._ev[e], s, e)
        self._forest[l].setEdgeMark(s, True)

    # the heart of HDLT: hunt for an edge that reconnects the two halves
    def _replace(self, l, u, v):
        f = self._forest[l]
        a = u if f.treeSize(u) <= f.treeSize(v) else v  # always walk the smaller half, so a promotion doubles a component
        ra = f.rootOf(a)

        # every level-l tree edge of the smaller half moves up to level l + 1
        treeEdges = []
        f.gather(ra, 0, treeEdges)
        for x in treeEdges:
            e = f.eid[x]
            s = self._slot[e]
            f.setEdgeMark(s, False)
            self._elevel[e] = l + 1
            self._forest[l + 1].link(self._eu[e], self._ev[e], s, e)
            self._forest[l + 1].setEdgeMark(s, True)

        # scan level-l non-tree edges out of the smaller half, stopping at the first one that crosses over
        verts = []
        f.gather(ra, 1, verts)
        promote = []
        rep = -1
        for x in verts:
            arc = self._head[l][x - 1]
            while arc != -1:
                e = arc >> 1
                if f.rootOf(self._other(arc)) != ra:
                    rep = e
                    break
                if not self._seen[e]:
                    self._seen[e] = True
                    promote.append(e)
                arc = self._nxt[arc]
            if rep != -1:
                break

        # everything we looked at and rejected has both ends inside the smaller half, so it moves up too
        for e in promote:
            self._seen[e] = False
            self._delArc(2 * e, l)
            self._delArc(2 * e + 1, l)
            self._elevel[e] = l + 1
            self._addArc(2 * e, l + 1)
            self._addArc(2 * e + 1, l + 1)

        if rep != -1:
            self._delArc(2 * rep, l)
            self._delArc(2 * rep + 1, l)
            self._makeTreeEdge(rep, l)
            return True
        return self._replace(l - 1, u, v) if l > 0 else False

    # O(log^2 n) amortized, returns an edge id you hand back to removeEdge
    def addEdge(self, u, v):
        e = self._newId()
        self._eu[e], self._ev[e], self._elevel[e], self._slot[e] = u, v, 0, -1
        self._byPair[(min(u, v), max(u, v))].append(e)
        if u == v:
            return e
        if not self._forest[0].sameTree(u, v):
            self._makeTreeEdge(e, 0)
            self._comps -= 1
        else:
            self._addArc(2 * e, 0)
            self._addArc(2 * e + 1, 0)
        return e

    # O(log^2 n) amortized, true if the component actually split in two
    def removeEdge(self, e):
        u, v, l, s = self._eu[e], self._ev[e], self._elevel[e], self._slot[e]
        split = False
        if s != -1:
            self._forest[l].setEdgeMark(s, False)
            for i in range(l + 1):
                self._forest[i].cut(s)
            self._slot[e] = -1
            self._freeSlots.append(s)
            split = not self._replace(l, u, v)
            if split:
                self._comps += 1
        elif u != v:
            self._delArc(2 * e, l)
            self._delArc(2 * e + 1, l)
        self._byPair[(min(u, v), max(u, v))].remove(e)
        self._freeIds.append(e)
        return split

    # O(log^2 n) amortized, removes one edge between u and v, false if there was none
    def removeEdgeBetween(self, u, v):
        ids = self._byPair[(min(u, v), max(u, v))]
        if not ids:
            return False
        self.removeEdge(ids[-1])
        return True

    # O(log n), true if u and v are in the same component
    def areConnected(self, u, v):
        return self._forest[0].sameTree(u, v)

    # O(log n), how many elements are in u's component
    def size(self, u):
        return self._forest[0].treeSize(u)

    # O(1), how many components exist right now
    def numComponents(self):
        return self._comps

    # O(log n), opaque handle shared by exactly the vertices of u's component, invalidated by the next update
    def componentId(self, u):
        return self._forest[0].rootOf(u)

    # O(n log n), one vertex index per component
    def roots(self):
        rep = {}
        for u in range(self.n):
            rep.setdefault(self.componentId(u), u)
        return list(rep.values())

    # O(n log n), the values grouped by component
    def groups(self):
        g = defaultdict(list)
        for u in range(self.n):
            g[self.componentId(u)].append(self.vals[u])
        return list(g.values())

    # O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    def sizes(self):
        cnt = defaultdict(int)
        for u in range(self.n):
            cnt[self.componentId(u)] += 1
        return sorted(cnt.values(), reverse=True)

    # O(n log n), the values of every element sitting in the same component as index u
    def elementsInGroup(self, u):
        r = self.componentId(u)
        return [self.vals[j] for j in range(self.n) if self.componentId(j) == r]