class TreeDistance:
    def __init__(self, n, edges, root=0):
        self.n = n
        self.root = root
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        self.depths = [-1] * n
        self.parents = [0] * n
        self.depths[root] = 0
        self.parents[root] = root

        q = deque([root])
        while q:
            node = q.popleft()
            for nxt in adj[node]:
                if self.depths[nxt] != -1:
                    continue
                self.depths[nxt] = self.depths[node] + 1
                self.parents[nxt] = node
                q.append(nxt)

        self.log = max(1, (n - 1).bit_length())
        self.lift = [[0] * self.log for _ in range(n)]
        for i in range(n):
            self.lift[i][0] = self.parents[i]
        self.lift[root][0] = root
        for jumpPow in range(1, self.log):
            for node in range(n):
                mid = self.lift[node][jumpPow - 1]
                self.lift[node][jumpPow] = self.lift[mid][jumpPow - 1]

    def getKthAncestor(self, node, k):
        result = node
        bit = 0
        while k:
            if k & 1:
                result = self.lift[result][bit]
            k >>= 1
            bit += 1
        return result

    def getLca(self, u, v):
        if self.depths[u] < self.depths[v]:
            u, v = v, u
        u = self.getKthAncestor(u, self.depths[u] - self.depths[v])
        if u == v:
            return u
        for jumpPow in range(self.log - 1, -1, -1):
            if self.lift[u][jumpPow] != self.lift[v][jumpPow]:
                u = self.lift[u][jumpPow]
                v = self.lift[v][jumpPow]
        return self.parents[u]

    def getDistance(self, a, b):
        lca = self.getLca(a, b)
        return self.depths[a] + self.depths[b] - 2 * self.depths[lca]
        
class Solution:
    def specialNodes(self, n: int, edges: List[List[int]], x: int, y: int, z: int) -> int:
        def isp(d1, d2, d3):
            arr = [d1, d2, d3]
            arr.sort()
            if arr[0]**2 + arr[1]**2 == arr[2]**2:
                return True
            return False

        td = TreeDistance(n, edges)

        res = 0
        for node in range(n):
            d1 = td.getDistance(node, x)
            d2 = td.getDistance(node, y)
            d3 = td.getDistance(node, z)
            if isp(d1, d2, d3):
                res += 1

        return res
            
            

        