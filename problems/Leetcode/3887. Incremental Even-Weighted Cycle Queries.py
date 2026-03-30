class WeightedDSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.dist = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            root = self.find(self.parent[x])
            self.dist[x] += self.dist[self.parent[x]]
            self.parent[x] = root
        return self.parent[x]

    def distToRoot(self, x):
        self.find(x)
        return self.dist[x]

    def union(self, x, y, w):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return self.dist[x] - self.dist[y] == w
        if self.rank[rx] < self.rank[ry]:
            rx, ry, x, y, w = ry, rx, y, x, -w
        self.parent[ry] = rx
        self.dist[ry] = self.dist[x] - self.dist[y] - w
        if self.rank[rx] == self.rank[ry]:
            self.rank[rx] += 1
        return True
        
class Solution:
    def numberOfEdgesAdded(self, n: int, edges: List[List[int]]) -> int:
        res = 0
        uf = WeightedDSU(n)
        for i, (a, b, w) in enumerate(edges):
            if uf.find(a) != uf.find(b):
                uf.union(a, b, w)
                res += 1
                continue
            ndist = uf.distToRoot(a) + uf.distToRoot(b) + w
            if ndist % 2:
                continue
            uf.union(a,b,w)
            res += 1
        return res