n, m = map(int, input().split())
edges = []
for _ in range(m):
    a, b = map(int, input().split())
    edges.append((a - 1, b - 1))

class DSU:
    def __init__(self, n):
        self.parents = [i for i in range(n)] # maps a node to its representative
        self.sz = [1] * n # sizes of represenative components
    
    def find(self, x):
        # path compression
        while x != self.parents[x]:
            self.parents[x] = self.parents[self.parents[x]]
            x = self.parents[x]
        return x
        
    def union(self, a, b):
        p1 = self.find(a)
        p2 = self.find(b)
        if p1 == p2:
            return False
        s1 = self.sz[p1]
        s2 = self.sz[p2]
        if s1 <= s2:
            self.parents[p1] = p2
            self.sz[p2] += self.sz[p1]
        else:
            self.parents[p2] = p1
            self.sz[p1] += self.sz[p2]
        return True

dsu = DSU(n)
for a, b in edges:
    dsu.union(a, b)

roots = set(dsu.find(i) for i in range(n))
componentSizes = sorted([dsu.sz[r] for r in roots])

counts = [0] * (n + 1) # counts of every size
for c in componentSizes:
    counts[c] += 1

bundles = [] # will hold (componentSize, numberOfMergesNeededForThis)
for sz in range(1, n + 1):
    countThatSize = counts[sz] # we need to binary decomp this option
    power = 0
    curr = countThatSize
    while curr:
        bundleSizeHere = min(curr, 2**power)
        totalIslandBundleSize = sz * bundleSizeHere
        merges = bundleSizeHere - 1
        bundles.append((totalIslandBundleSize, merges))
        power += 1
        curr -= bundleSizeHere

INF = 1 * 10**18
dp = [INF] * (n + 1) # min bridges needed to make a component of that size
dp[0] = 0 # dp array is the answer BEFORE we process any elements, so we should not set base cases for all our existing components to 0
# that sounds right, but would pollute the answer since we assume we can reach for example a component of size 2 with 0 cost, then when we encounter our size 2 bundle, we erroneously double count it

for nodeSize, cost in bundles:
    ndp = dp[:]
    for sz in range(n + 1):
        mergedSize = sz + nodeSize
        if mergedSize > n:
            break
        ndp[mergedSize] = min(ndp[mergedSize], dp[sz] + cost + (1 if sz else 0))
    dp = ndp

res = INF
for sz in range(n + 1):
    if any(c not in '47' for c in str(sz)):
        continue
    res = min(res, dp[sz])

if res == INF:
    print(-1)
else:
    print(res)


