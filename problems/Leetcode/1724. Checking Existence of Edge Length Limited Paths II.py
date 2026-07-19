# SOLUTION 1, MSTS + JUMP TABLES
# dsu = DSU(arr)
# takes an array of values (can be array of strings, tuples, etc) since everything operates on indices

class DSU:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0

    # O(1), index of the representative of i's component
    def find(self, i):
        par = self.par
        while par[i] != i:
            par[i] = par[par[i]]
            i = par[i]
        return i

    # O(1), merges the two components, False if i and j were already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return False
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[i])
        return True

    # O(1), True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(1), how many elements are in i's component
    def size(self, i):
        return self.sz[self.find(i)]

    # O(1), how many components exist right now
    def numComponents(self):
        return self.comps

    # O(1), size of the biggest component, maintained in unite
    def largestSize(self):
        return self.mx

    # O(n), one index per component: the representative each member's find returns
    def roots(self):
        return [i for i in range(len(self.par)) if self.par[i] == i]

    # O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    def sizes(self):
        return sorted((self.sz[i] for i in range(len(self.par)) if self.par[i] == i), reverse=True)

    # O(n), groupsArr[rt] = list of values whose root is rt, [] if rt is not a root
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            rt = self.find(i)
            groupsArr[rt].append(self.vals[i])
        return groupsArr

    # O(n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]


# TEMPLATE BY ISHAANBUILDSTHINGS
# root = the root node (usually 0 or 1)
# edges = [[a, b, rawVal], [c, d, rawVal], ...] where rawVal is the raw data for the edge a<>b
# base = (rawEdge) -> mapped val
# merge(edgeVal1, edgeVal2) -> edgeVal3
class LiftEdge:
    # O(n log n) build time and space
    def __init__(self, root, edges, base, merge):
        self.n = root
        for u, v, w in edges:
            self.n = max(self.n, u, v)
        self.n += 1
        self.LOG = max(1, self.n.bit_length())
        self.base = base
        self.merge = merge

        g = [[] for _ in range(self.n)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))

        self.depths = [0] * self.n
        self.up = [[0] * self.n for _ in range(self.LOG)]
        self.upData = [[None] * self.n for _ in range(self.LOG)]

        stack = [(root, root, None, False)]
        while stack:
            node, parent, valAbove, visited = stack.pop()
            if visited:
                continue
            self.depths[node] = 0 if node == root else self.depths[parent] + 1
            self.up[0][node] = parent
            if node != root:
                self.upData[0][node] = base(valAbove)
            for k in range(1, self.LOG):
                mid = self.up[k - 1][node]
                self.up[k][node] = self.up[k - 1][mid]
                a = self.upData[k - 1][node]
                b = self.upData[k - 1][mid]
                if a is None:
                    self.upData[k][node] = b
                elif b is None:
                    self.upData[k][node] = a
                else:
                    self.upData[k][node] = merge(a, b)
            stack.append((node, parent, valAbove, True))
            for child, childVal in g[node]:
                if child != parent:
                    stack.append((child, node, childVal, False))

    # kth steps above `node`
    # always returns root if k steps shoots past the root
    # O(log N)
    def kthAncestor(self, node, kth):
        for k in range(self.LOG):
            if (kth >> k) & 1:
                node = self.up[k][node]
        return node

    # O(log N)
    def lca(self, a, b):
        if self.depths[a] < self.depths[b]:
            a, b = b, a
        diff = self.depths[a] - self.depths[b]
        for k in range(self.LOG):
            if (diff >> k) & 1:
                a = self.up[k][a]
        if a == b:
            return a
        for k in range(self.LOG - 1, -1, -1):
            if self.up[k][a] != self.up[k][b]:
                a = self.up[k][a]
                b = self.up[k][b]
        return self.up[0][a]

    # unweighted path distance from A<>B
    # O(log N)
    def pathDist(self, a, b):
        ab = self.lca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[ab]

    # the median node, which is the only node on all three paths: A<>B, B<>C, A<>C
    # O(log N)
    def median(self, a, b, c):
        return self.lca(a, b) ^ self.lca(a, c) ^ self.lca(b, c)

    # k-th node on the A->B path, 1-indexed
    # -1 if OOB
    # O(log N)
    def kthOnPath(self, a, b, kth):
        ab = self.lca(a, b)
        distA = self.depths[a] - self.depths[ab]
        distB = self.depths[b] - self.depths[ab]
        totalLen = distA + distB + 1
        if kth < 1 or kth > totalLen:
            return -1
        if kth <= distA + 1:
            return self.kthAncestor(a, kth - 1)
        return self.kthAncestor(b, distB - (kth - distA - 1))

    # how many edges to cross to get from `node` onto any node on the A<>B path
    # O(log N)
    def distToPath(self, a, b, node):
        return self.pathDist(self.median(a, b, node), node)

    # returns a bool if `node` is on the path A<>B
    # O(log N)
    def inPath(self, a, b, node):
        return self.median(a, b, node) == node

    # aggregated edgeValue for the k edges going up from `node` (edge above node first), None if k==0
    # O(log N)
    def liftQuery(self, node, k):
        acc = None
        rem = k
        for b in range(self.LOG - 1, -1, -1):
            if rem >= (1 << b):
                d = self.upData[b][node]
                if d is not None:
                    acc = d if acc is None else self.merge(acc, d)
                node = self.up[b][node]
                rem -= (1 << b)
        return acc

    # aggregated edgeValue for the A<>B path (edge above the LCA is NOT on the path); None if A==B
    # O(log N)
    def pathQuery(self, a, b):
        l = self.lca(a, b)
        da = self.depths[a] - self.depths[l]
        db = self.depths[b] - self.depths[l]
        left = self.liftQuery(a, da) if da > 0 else None
        right = self.liftQuery(b, db) if db > 0 else None
        if left is None:
            return right
        if right is None:
            return left
        return self.merge(left, right)

    # lca of a and b if the tree were rooted at r instead of the build root
    # O(log N)
    def lcaUnderR(self, r, a, b):
        return self.median(a, b, r)

    # intersection of path a<>b and path x<>y (endpoint order doesn't matter).
    # returns (p, q), the endpoints of the shared subpath (p == q if a single node),
    # or None if the two paths are disjoint.
    # O(log N)
    def pathIntersection(self, a, b, x, y):
        cands = [
            self.median(a, b, x), self.median(a, b, y),
            self.median(x, y, a), self.median(x, y, b),
        ]
        onBoth = [c for c in cands
                  if self.inPath(a, b, c) and self.inPath(x, y, c)]
        if not onBoth:
            return None
        p = q = onBoth[0]
        best = -1
        for i in range(len(onBoth)):
            for j in range(i, len(onBoth)):
                d = self.pathDist(onBoth[i], onBoth[j])
                if d > best:
                    best = d
                    p, q = onBoth[i], onBoth[j]
        return (p, q)


class DistanceLimitedPathsExist:

    def __init__(self, n: int, edgeList: List[List[int]]):
        dsu = DSU([i for i in range(n + 1)])
        edgeList.sort(key=lambda tup: tup[-1])
        usedEdges = [] # (a, b, w)
        for a, b, w in edgeList:
            if dsu.areUnioned(a, b): continue
            dsu.unite(a, b)
            usedEdges.append((a, b, w))
        
        components = [x for x in dsu.groups() if x]

        superRoot = n
        for comp in components:
            fakeEdge = (superRoot, comp[0], inf)
            dsu.unite(superRoot, comp[0])
            usedEdges.append(fakeEdge)

        self.dsu = dsu
        self.lifter = LiftEdge(superRoot, usedEdges, lambda x : x, max)
        
    def query(self, p: int, q: int, limit: int) -> bool:
        mx = self.lifter.pathQuery(p, q)
        return mx < limit
        

        
        


# Your DistanceLimitedPathsExist object will be instantiated and called as such:
# obj = DistanceLimitedPathsExist(n, edgeList)
# param_1 = obj.query(p,q,limit)








# SOLUTION 2, CRAZY UNION FIND
# dsu = DSUNoCompress(arr)
# takes an array of values (can be array of strings, tuples, etc) since everything operates on indices

class DSUNoCompress:
    # O(n), every element starts in its own component
    def __init__(self, vals):
        self.vals = list(vals)
        n = len(self.vals)
        self.par = list(range(n))
        self.sz = [1] * n
        self.comps = n
        self.mx = 1 if n else 0

    # O(log n), index of the representative of i's component, parents left untouched
    def find(self, i):
        par = self.par
        while par[i] != i:
            i = par[i]
        return i

    # O(log n), merges the two components, returns (winner, loser) or None if already together
    def unite(self, i, j):
        i, j = self.find(i), self.find(j)
        if i == j:
            return None
        if self.sz[i] < self.sz[j]:
            i, j = j, i
        self.par[j] = i
        self.sz[i] += self.sz[j]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[i])
        return i, j

    # O(log n), forces a's root under b's root, False if already together
    # skips union by size, so depth can degrade to O(n) and every walk with it
    def uniteAUnderB(self, a, b):
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.par[a] = b
        self.sz[b] += self.sz[a]
        self.comps -= 1
        self.mx = max(self.mx, self.sz[b])
        return True

    # O(log n), True if i and j are in the same component
    def areUnioned(self, i, j):
        return self.find(i) == self.find(j)

    # O(log n), how many elements are in i's component
    def size(self, i):
        return self.sz[self.find(i)]

    # O(1), how many components exist right now
    def numComponents(self):
        return self.comps

    # O(1), size of the biggest component, maintained in unite
    def largestSize(self):
        return self.mx

    # O(n), one index per component: the representative each member's find returns
    def roots(self):
        return [i for i in range(len(self.par)) if self.par[i] == i]

    # O(n log n), the sizes of all components, biggest first, e.g. [4, 2, 1]
    def sizes(self):
        return sorted((self.sz[i] for i in range(len(self.par)) if self.par[i] == i), reverse=True)

    # O(n log n), groupsArr[rt] = list of values whose root is rt, [] if rt is not a root
    def groups(self):
        n = len(self.par)
        groupsArr = [[] for _ in range(n)]
        for i in range(n):
            rt = self.find(i)
            groupsArr[rt].append(self.vals[i])
        return groupsArr

    # O(n log n), the values of every element sitting in the same group as index i
    def elementsInGroup(self, i):
        rt = self.find(i)
        return [self.vals[j] for j in range(len(self.par)) if self.find(j) == rt]
class DistanceLimitedPathsExist:

    def __init__(self, n: int, edgeList: List[List[int]]):
        edgeList.sort(key=lambda x : x[-1])
        dsu = DSUNoCompress(list(range(n)))
        stamps = [None] * n
        for a, b, w in edgeList:
            if dsu.areUnioned(a, b):
                continue
            s1 = dsu.size(a)
            s2 = dsu.size(b)
            ra = dsu.find(a)
            rb = dsu.find(b)
            if s1 <= s2:
                dsu.uniteAUnderB(ra, rb)
                stamps[ra] = w
            else:
                dsu.uniteAUnderB(rb, ra)
                stamps[rb] = w
        self.dsu = dsu
        self.stamps = stamps

    def query(self, p: int, q: int, limit: int) -> bool:
        if not self.dsu.areUnioned(p, q):
            return False
        currP = p
        currQ = q
        # walk up while we can
        while self.stamps[currP] is not None and self.stamps[currP] < limit:
            currP = self.dsu.par[currP]
        while self.stamps[currQ] is not None and self.stamps[currQ] < limit:
            currQ = self.dsu.par[currQ]
        return currP == currQ
        
        


# Your DistanceLimitedPathsExist object will be instantiated and called as such:
# obj = DistanceLimitedPathsExist(n, edgeList)
# param_1 = obj.query(p,q,limit)