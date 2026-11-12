# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/trees/weightedEdgeListToTree.py
# TEMPLATE BY ISHAAN AGRAWAL, github: ishaanbuildsthings
# edgeList = [[a, b, w], [c, d, w], ...]
# roots the tree at `root` (any node id) and returns `children`, sized to fit the largest label 0-indexed input ->
# children goes up to children[n-1]; 1-indexed -> up to children[n], children[0] empty and unused
# children[node] = [(child, weight), ...] where weight is the edge from node to child
def edgeListToTree(edgeList, root):
    size = max([root] + [max(a, b) for a, b, _ in edgeList]) + 1
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
