# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/articulationPoints.py

# cutNodes = articulationPoints(edges)
#   edges is a list of undirected edges [[node1, node2], ...]; repeated edges and
#   self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)
#   For example: articulationPoints([[1, 2], [2, 3], [3, 1], [3, 4], [4, 5]])
#
# cutNodes -> every node that, if removed with its edges, splits its component into two or more
#   pieces, increasing, e.g. [3, 4]
#
#   Here removing 3 separates the triangle's 1 and 2 from 4 and 5, and removing 4 cuts 5 off.
#   Removing 1 or 2 leaves everything else connected
#
#   articulationPoints([[1, 2], [1, 3], [1, 4]]) -> [1]    (removing the center leaves three pieces)
#
# O(V + E) time and space, V = largest label, E = number of edges


def articulationPoints(edges):
    size = 0
    for node1, node2 in edges:
        if node1 < 0 or node2 < 0:
            raise ValueError(f"articulationPoints: edge ({node1}, {node2}) has a negative label")
        size = max(size, node1 + 1, node2 + 1)
    adj = [[] for _ in range(size)]
    for edgeId, (node1, node2) in enumerate(edges):
        adj[node1].append((node2, edgeId))
        adj[node2].append((node1, edgeId))

    # depth-first search: low[node] = the earliest entry time reachable from node's subtree using one back edge.
    # A non-root node cuts the graph when some child's subtree can't reach above it; the root cuts it when it has
    # two or more children in the search
    tin = [-1] * size
    low = [0] * size
    nextIdx = [0] * size
    parentEdge = [-1] * size
    isCut = [False] * size
    timer = 0
    for root in range(size):
        if tin[root] != -1:
            continue
        tin[root] = low[root] = timer
        timer += 1
        rootChildren = 0
        stack = [root]
        while stack:
            node = stack[-1]
            if nextIdx[node] < len(adj[node]):
                nxt, edgeId = adj[node][nextIdx[node]]
                nextIdx[node] += 1
                if edgeId == parentEdge[node]:
                    continue
                if tin[nxt] == -1:
                    parentEdge[nxt] = edgeId
                    tin[nxt] = low[nxt] = timer
                    timer += 1
                    stack.append(nxt)
                elif tin[nxt] < low[node]:
                    low[node] = tin[nxt]
            else:
                stack.pop()
                if stack:
                    par = stack[-1]
                    if low[node] < low[par]:
                        low[par] = low[node]
                    if par == root:
                        rootChildren += 1
                    elif low[node] >= tin[par]:
                        isCut[par] = True
        if rootChildren >= 2:
            isCut[root] = True
    return [node for node in range(size) if isCut[node]]
