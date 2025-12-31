import functools
# TEMPLATE
# unions by depth

class DSU:
    def __init__(self, nodes):
        self.parents = {} # maps a node to SOME parent, depends on the current amount of path compression, doesn't always map directly to the representative parent, may need to follow a chain
        self.depths = {} # maps the representative parent to its depth
        for node in nodes:
            self.parents[node] = node
            self.depths[node] = 1

    # finds the representative parent for a node and path compresses
    # def _find(self, node):
    # TODO: check path compression applies to everything
    #     while self.parents[node] != node:
    #         parent = self.parents[node]
    #         doubleParent = self.parents[parent]
    #         self.parents[node] = doubleParent
    #         node = doubleParent
    #     return node
    def _find(self, node):
      if self.parents[node] != node:
          self.parents[node] = self._find(self.parents[node])
      return self.parents[node]

    # unions two nodes, returns true/false inf successful
    def union(self, a, b):
        aRepParent = self._find(a)
        bRepParent = self._find(b)
        # if they are the same, they are already unioned
        if aRepParent == bRepParent:
            return False

        aDepth = self.depths[aRepParent]
        bDepth = self.depths[bRepParent]
        # bring a under b
        if aDepth < bDepth:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
        elif bDepth < aDepth:
            self.parents[bRepParent] = aRepParent
            del self.depths[bRepParent]
        else:
            self.parents[aRepParent] = bRepParent
            del self.depths[aRepParent]
            self.depths[bRepParent] += 1
        return True

    def areUnioned(self, a, b):
        return self._find(a) == self._find(b)

    def uniqueComponents(self):
        return len(self.depths)


def floydWarshallFromAdj(n, g):
    inf = 10**30
    dist = [[inf] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u in range(n):
        for v, w in g[u]:
            if w < dist[u][v]:
                dist[u][v] = w
    for k in range(n):
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik >= inf:
                continue
            di = dist[i]
            for j in range(n):
                nd = dik + dk[j]
                if nd < di[j]:
                    di[j] = nd
    return dist


n, m = map(int, input().split())
res = 0

notIslandNodes = set()
edges = [] # holds (a, b, w), first checking to remove empty island nodes since they won't affect the answer
for _ in range(m):
    a, b, w = map(int, input().split())
    notIslandNodes.add(a-1)
    notIslandNodes.add(b-1)
    edges.append([a-1,b-1,w])

# if the root is an island, we only succeed if there are no edges
if 0 not in notIslandNodes:
    if not edges:
        print(0)
    else:
        print(-1)
    exit()

nodes = []
for node in range(n):
    if node in notIslandNodes:
        nodes.append(node)
dsu = DSU(nodes)
g = [[] for _ in range(n)]


for a, b, w in edges:
    if a == b:
        res += w
    else:
        res += w
        g[a].append((b,w))
        g[b].append((a,w))
        dsu.union(a,b)
if dsu.uniqueComponents() != 1:
    # print(f'more than one component in graph')
    # edge case, graph of just empty nodes, no edges need to be traveled
    if not res:
        print('0')
    else:
        print('-1')
    exit()

oddNodes = []
for node in range(len(g)):
    if len(g[node]) % 2:
        oddNodes.append(node)

fw = floydWarshallFromAdj(len(g), g) # fw[node1][node2] = min dist

fmask = (1 << len(oddNodes)) - 1
@functools.lru_cache
def dp(mask):
    if mask == fmask:
        return 0
    lusb = None
    for i in range(len(oddNodes)):
        if not mask & (1 << i):
            lusb = i
            break
    resHere = float('inf')
    # the lusb needs to get paired with something
    for j in range(i + 1, len(oddNodes)):
        if not mask & (1 << j):
            nmask = mask | (1 << lusb) | (1 << j)
            minWeight = fw[oddNodes[lusb]][oddNodes[j]]
            resHere = min(resHere, minWeight + dp(nmask))
    return resHere


print(dp(0) + res)

    

