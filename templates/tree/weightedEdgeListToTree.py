# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings

# edgeList = [[a, b, w], [c, d, w], ...]
# if zeroIndex is true, assumes the root is 0, returns an array `children` that goes up to `children[n-1]` (n-1 is inferred from the edgeList)
# if zeroIndex is false, assumes the root is 1, returns an array `children` that goes up to `children[n]`, children[0] is empty and unused
# children[node] = [(child, weight), ...] where weight is the edge from node to child
def edgeListToTree(edgeList, zeroIndexed=True):
    n = len(edgeList) + 1
    size = n if zeroIndexed else n + 1
    root = 0 if zeroIndexed else 1
    edgeMap = [[] for _ in range(size)]
    for a, b, w in edgeList:
        edgeMap[a].append((b, w))
        edgeMap[b].append((a, w))
    children = [[] for _ in range(size)]
    parent = [-1] * size
    stack = [root]
    while stack:
        node = stack.pop()
        for adj, w in edgeMap[node]:
            if adj == parent[node]:
                continue
            parent[adj] = node
            children[node].append((adj, w))
            stack.append(adj)
    return children