import random
# TEMPLATE BY ISHAANBUILDSTHINGS on github
# in:  edgeList  = [(1,2), (1,3), (2,4), (2,5)]   # unrooted, labels can be 0- or 1-indexed
# out: centroids = [2] or [1, 2]   # 1 or 2 nodes, sorted; deleting one leaves every piece <= n/2
# O(n) time, O(n) space
def findCentroids(edgeList):
    n = len(edgeList) + 1
    size = max(max(a, b) for a, b in edgeList) + 1
    start = edgeList[0][0]
    edgeMap = [[] for _ in range(size)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)
    order = []
    parent = [-1] * size
    stk = [start]
    while stk:
        node = stk.pop()
        order.append(node)
        for adj in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            stk.append(adj)
    subtreeSize = [0] * size
    maxComponent = [0] * size
    for node in reversed(order):
        subtreeSize[node] += 1
        maxComponent[node] = max(maxComponent[node], n - subtreeSize[node])
        if parent[node] != -1:
            subtreeSize[parent[node]] += subtreeSize[node]
            maxComponent[parent[node]] = max(maxComponent[parent[node]], subtreeSize[node])
    best = min(maxComponent[node] for node in order)
    return sorted(node for node in order if maxComponent[node] == best)


# TEMPLATE BY ISHAANBUILDSTHINGS on github

MASK = (1 << 64) - 1
FIXED = random.getrandbits(64)

def mix(x):
    x = (x + 0x9e3779b97f4a7c15 + FIXED) & MASK
    x = ((x ^ (x >> 30)) * 0xbf58476d1ce4e5b9) & MASK
    x = ((x ^ (x >> 27)) * 0x94d049bb133111eb) & MASK
    return x ^ (x >> 31)

# in:  children = [[], [2,3], [4,5], [], [], []]   # children[v], parent excluded; root matches indexing
# out: hashes   = [0, h1, h2, mix1, mix1, mix1]    # hashes[v] = 64-bit hash of v's subtree
# hashes[u] == hashes[v] iff those subtrees are isomorphic as rooted unordered trees. O(n log n) time, O(n) space
def subtreeHashes(children, root):
    hashes = [0] * len(children)
    order = []
    stk = [root]
    while stk:
        node = stk.pop()
        order.append(node)
        stk.extend(children[node])
    for node in reversed(order):
    #     h = 1
    #     for childHash in sorted(hashes[child] for child in children[node]):
    #         h = (h * 1000000007 + childHash) & MASK
    #     # hashes[node] = mix(h)
        hashes[node] = hash(tuple(sorted([hashes[child] for child in children[node]])))
    return hashes

    # TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# edgeList = [[a, b], [c, d], ...]
# roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label
# 0-indexed input -> children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
def edgeListToTree(edgeList, root):
    size = max(max(a, b) for a, b in edgeList) + 1
    edgeMap = [[] for _ in range(size)]
    for a, b in edgeList:
        edgeMap[a].append(b)
        edgeMap[b].append(a)
    children = [[] for _ in range(size)]
    parent = [-1] * size
    stack = [root]
    while stack:
        node = stack.pop()
        for adj in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            children[node].append(adj)
            stack.append(adj)
    return children

import sys
data = sys.stdin.buffer.read().split()
pos = 0
def nextInt():
    global pos
    pos += 1
    return int(data[pos - 1])

def solve():
    n = nextInt()
    edges1 = []
    for _ in range(n - 1):
        a, b = nextInt(), nextInt()
        edges1.append((a, b))
    edges2 = []
    for _ in range(n - 1):
        a, b = nextInt(), nextInt()
        edges2.append((a, b))

    centroids1 = findCentroids(edges1)
    centroids2 = findCentroids(edges2)


    hashes1 = []
    for centroid in centroids1:
        children = edgeListToTree(edges1, centroid)
        allHashes = subtreeHashes(children, centroid)
        hashes1.append(allHashes[centroid])
    
    hashes2 = []
    for centroid in centroids2:
        children = edgeListToTree(edges2, centroid)
        allHashes = subtreeHashes(children, centroid)
        hashes2.append(allHashes[centroid])
    
    if set(hashes1) & set(hashes2):
        print('YES')
    else:
        print('NO')

    
t = nextInt()
for _ in range(t):
    solve()