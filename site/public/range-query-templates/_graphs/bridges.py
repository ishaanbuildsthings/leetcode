# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/bridges.py

# bridgeEdges = bridges(edges)
#   edges is a list of undirected edges [[node1, node2], ...]; repeated edges and
#   self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   (a node with no edges can't affect the answer, so how many nodes there are doesn't matter)
#   For example: bridges([[1, 2], [2, 3], [3, 1], [3, 4], [4, 5], [4, 5]])
#
# bridgeEdges -> every edge that, if removed, splits its component in two, e.g. [[3, 4]]
#   Each edge is written exactly as you gave it, in the order you gave them
#
#   Here 1, 2, 3 form a triangle, so removing any one of those edges still leaves another way
#   around. Removing 3 - 4 cuts 4 and 5 off. 4 - 5 is listed twice, so neither copy is a bridge:
#   the other copy still connects them
#
#   bridges([[1, 2], [2, 3]]) -> [[1, 2], [2, 3]]    (in a tree, every edge is a bridge)
#
# O(V + E) time and space, V = number of nodes, E = number of edges


def bridges(edges):
    size = 0
    for node1, node2 in edges:
        if node1 < 0 or node2 < 0:
            raise ValueError(f"bridges: edge ({node1}, {node2}) has a negative label")
        size = max(size, node1 + 1, node2 + 1)
    adj = [[] for _ in range(size)]
    for edgeId, (node1, node2) in enumerate(edges):
        adj[node1].append((node2, edgeId))
        adj[node2].append((node1, edgeId))

    # depth-first search: low[node] = the earliest entry time reachable from node's subtree using one back edge.
    # The edge into a child is a bridge when nothing below the child reaches back above it
    tin = [-1] * size
    low = [0] * size
    nextIdx = [0] * size
    parentEdge = [-1] * size
    isBridge = [False] * len(edges)
    timer = 0
    for root in range(size):
        if tin[root] != -1:
            continue
        tin[root] = low[root] = timer
        timer += 1
        stack = [root]
        while stack:
            node = stack[-1]
            if nextIdx[node] < len(adj[node]):
                nxt, edgeId = adj[node][nextIdx[node]]
                nextIdx[node] += 1
                if edgeId == parentEdge[node]:  # skip only that one edge, so a repeated edge counts as a way back
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
                    if low[node] > tin[par]:
                        isBridge[parentEdge[node]] = True
    return [list(edges[i]) for i in range(len(edges)) if isBridge[i]]
