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