# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallUndirected.py

# Floyd-Warshall, undirected graph, 0-indexed: shortest distance between every pair of nodes.
# numNodes: how many nodes there are; the nodes are 0..numNodes - 1. (A node with no edges never shows up
# in the edge list, so the count has to be passed.)
# edges: [a, b, w] meaning a <-> b, usable both ways, with weight w >= 0. Repeated edges keep the cheapest; self-loops
# are ignored. A negative weight is an error (a negative loop would make some distances meaningless).
# Returns dist, a numNodes x numNodes matrix: dist[a][b] = the shortest distance from a to b, INF if b
# can't be reached from a, 0 for a to itself.
# Example:
#   dist = floydWarshallUndirected(4, [(0, 1, 4), (0, 2, 1), (2, 1, 2)])
#   dist[0] -> [0, 3, 1, INF]    0 -> 1 costs 3 (through 2); node 3 has no edges, so it's INF
#   dist[1] -> [3, 0, 2, INF]
# O(V^3 + E) time, O(V^2) space, V = numNodes, E = number of edges. Negative weights raise ValueError.

INF = float('inf')  # what unreachable pairs hold


def floydWarshallUndirected(numNodes, edges):
    size = numNodes
    dist = [[INF] * size for _ in range(size)]
    for node in range(0, size):
        dist[node][node] = 0
    for a, b, w in edges:
        if not (0 <= a < size and 0 <= b < size):
            raise ValueError(f"floydWarshallUndirected: edge ({a}, {b}) is outside the nodes 0..{size - 1}")
        if w < 0:
            raise ValueError(f"floydWarshallUndirected: edge ({a}, {b}) has negative weight {w}")
        if w < dist[a][b]:
            dist[a][b] = w
        if w < dist[b][a]:
            dist[b][a] = w
    # allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper
    for mid in range(0, size):
        midRow = dist[mid]
        for a in range(0, size):
            row = dist[a]
            toMid = row[mid]
            if toMid == INF:
                continue
            for b in range(0, size):
                through = toMid + midRow[b]
                if through < row[b]:
                    row[b] = through
    return dist
