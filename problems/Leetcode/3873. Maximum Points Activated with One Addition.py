class DSU:
    def __init__(self, nodes):
        self.parents = {}
        self.depths = {}
        self.sizes = {}
        for node in nodes:
            self.parents[node] = node
            self.depths[node] = 1
            self.sizes[node] = 1

    def _find(self, node):
        if self.parents[node] != node:
            self.parents[node] = self._find(self.parents[node])
        return self.parents[node]

    def union(self, a, b):
        aRepParent = self._find(a)
        bRepParent = self._find(b)
        if aRepParent == bRepParent:
            return False
        aDepth = self.depths[aRepParent]
        bDepth = self.depths[bRepParent]
        if aDepth < bDepth:
            self.parents[aRepParent] = bRepParent
            self.sizes[bRepParent] += self.sizes[aRepParent]
            del self.depths[aRepParent]
            del self.sizes[aRepParent]
        elif bDepth < aDepth:
            self.parents[bRepParent] = aRepParent
            self.sizes[aRepParent] += self.sizes[bRepParent]
            del self.depths[bRepParent]
            del self.sizes[bRepParent]
        else:
            self.parents[aRepParent] = bRepParent
            self.sizes[bRepParent] += self.sizes[aRepParent]
            del self.depths[aRepParent]
            del self.sizes[aRepParent]
            self.depths[bRepParent] += 1
        return True

    def areUnioned(self, a, b):
        return self._find(a) == self._find(b)

    def uniqueComponents(self):
        return len(self.depths)

    def getSize(self, node):
        return self.sizes[self._find(node)]

    def allSizes(self):
        return list(self.sizes.values())


class Solution:
    def maxActivated(self, points: list[list[int]]) -> int:
        xs = defaultdict(list)
        ys = defaultdict(list)
        for x, y in points:
            xs[x].append((x,y))
            ys[y].append((x,y))
        points2 = []
        for point in points:
            points2.append(tuple(point))
        uf = DSU(points2)
        for xKey in xs:
            vs = xs[xKey]
            for i in range(len(vs) - 1):
                uf.union(vs[i],vs[i+1])
        for yKey in ys:
            vs = ys[yKey]
            for i in range(len(vs) - 1):
                uf.union(vs[i],vs[i+1])

        print(uf.uniqueComponents())

        # adding at an X gives us a single group that has that X, and we pick a Y
        # so pick top two groups?

        sz = sorted(uf.allSizes(),reverse=True)

        res = 1 + sz[0]
        if len(sz) > 1:
            res += sz[1]

        return res

        
            












        
        