# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallDirected.oneIndexed.py

# Floyd-Warshall, directed graph, 1-indexed: shortest distance between every pair of nodes.
# numNodes: how many nodes there are; the nodes are 1..numNodes. (A node with no edges never shows up
# in the edge list, so the count has to be passed.)
# edges: [a, b, w] meaning a -> b, with weight w >= 0. Repeated edges keep the cheapest; self-loops
# are ignored. A negative weight is an error (a negative loop would make some distances meaningless).
# Returns dist, a (numNodes + 1) x (numNodes + 1) matrix indexed by your labels: dist[a][b] = the shortest
# distance from a to b, INF if b can't be reached from a, 0 for a to itself.
# Node 0 doesn't exist: row 0 and column 0 are unused (all INF), ignore them.
# Example:
#   dist = floydWarshallDirected(4, [(1, 2, 4), (1, 3, 1), (3, 2, 2)])
#   dist[1] -> [INF, 0, 3, 1, INF]    1 -> 2 costs 3 (through 3); node 4 has no edges, so it's INF
#   dist[2] -> [INF, INF, 0, INF, INF]  nothing leaves 2
#   dist[0] -> [INF, INF, INF, INF, INF]  row 0 is unused
# O(V^3 + E) time, O(V^2) space, V = numNodes, E = number of edges. Negative weights raise ValueError.

INF = float('inf')  # what unreachable pairs hold


def floydWarshallDirected(numNodes, edges):
    size = numNodes + 1
    dist = [[INF] * size for _ in range(size)]
    for node in range(1, size):
        dist[node][node] = 0
    for a, b, w in edges:
        if not (1 <= a < size and 1 <= b < size):
            raise ValueError(f"floydWarshallDirected: edge ({a}, {b}) is outside the nodes 1..{size - 1}")
        if w < 0:
            raise ValueError(f"floydWarshallDirected: edge ({a}, {b}) has negative weight {w}")
        if w < dist[a][b]:
            dist[a][b] = w
    # allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper
    for mid in range(1, size):
        midRow = dist[mid]
        for a in range(1, size):
            row = dist[a]
            toMid = row[mid]
            if toMid == INF:
                continue
            for b in range(1, size):
                through = toMid + midRow[b]
                if through < row[b]:
                    row[b] = through
    return dist
