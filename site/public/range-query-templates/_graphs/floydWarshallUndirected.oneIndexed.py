# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallUndirected.oneIndexed.py

# dist = floydWarshallUndirected(numNodes, edges)
#   edges is a list of undirected weighted edges [[from, to, weight], ...], usable both ways, weights >= 0
#   Repeated edges keep the cheapest; self-loops are ignored
#   numNodes is how many nodes there are: the nodes are 1..numNodes
#   (a node with no edges never shows up in edges, so numNodes has to be passed)
#   For example: floydWarshallUndirected(4, [[1, 2, 4], [1, 3, 1], [3, 2, 2]])   (node 4 has no edges)
#
# dist[a][b] -> the shortest distance from a to b, e.g. dist[1] = [INF, 0, 3, 1, INF]
#   INF if b can't be reached from a, and 0 from a node to itself.
#   Here 1 -> 2 costs 3 by going through 3, instead of 4 directly
#   dist is a (numNodes + 1) x (numNodes + 1) matrix: node 0 doesn't exist, so row 0 and
#   column 0 are unused (all INF)
#
# INF -> float('inf'), set at the top of the file
#
# O(V^3 + E) time, O(V^2) space. Negative weights raise ValueError
# (a loop with negative total weight would make distances meaningless)

INF = float('inf')  # what unreachable pairs hold


def floydWarshallUndirected(numNodes, edges):
    size = numNodes + 1
    dist = [[INF] * size for _ in range(size)]
    for node in range(1, size):
        dist[node][node] = 0
    for a, b, w in edges:
        if not (1 <= a < size and 1 <= b < size):
            raise ValueError(f"floydWarshallUndirected: edge ({a}, {b}) is outside the nodes 1..{size - 1}")
        if w < 0:
            raise ValueError(f"floydWarshallUndirected: edge ({a}, {b}) has negative weight {w}")
        if w < dist[a][b]:
            dist[a][b] = w
        if w < dist[b][a]:
            dist[b][a] = w
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
