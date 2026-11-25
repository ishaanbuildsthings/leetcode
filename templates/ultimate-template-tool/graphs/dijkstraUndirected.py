# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/dijkstraUndirected.py

# Dijkstra, undirected graph: shortest distance from source to every node, plus the previous node on a shortest route.
# edges: [(a, b, w), ...] meaning a <-> b (both ways) with weight w >= 0 (ints or floats); repeated edges and
# self-loops are fine.
# n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is True. A node with no
# edges never shows up in the edge list, so n says how many there are; oneIndexed says where the labels start.
# Returns two lists, both indexed by your node labels:
#   dist[node]  the shortest distance from source to node; None if node can't be reached
#   prev[node]  the node a shortest route to node comes from, one step before it; None for the source itself and
#               for nodes that can't be reached
# With oneIndexed, index 0 isn't a node: dist[0] and prev[0] are just None placeholders, ignore them.
# To get the route itself, start at the target and keep stepping to prev until you reach the source (that walks it
# backwards).
# Example, 1-indexed: edges 1-2 (4), 1-3 (1), 3-2 (2), 2-4 (5), source 1
#   dist, prev = dijkstraUndirected([(1, 2, 4), (1, 3, 1), (3, 2, 2), (2, 4, 5)], 4, oneIndexed=True, source=1)
#   dist -> [None, 0, 3, 1, 8]      dist[4] = 8: the best route to 4 costs 1 + 2 + 5
#   prev -> [None, None, 3, 1, 2]   prev[4] = 2, prev[2] = 3, prev[3] = 1: the route is 1 -> 3 -> 2 -> 4
# O((V + E) log E) time, O(V + E) space, V = n, E = number of edges. Negative weights raise ValueError.
import heapq


def dijkstraUndirected(edges, n, oneIndexed: bool, source):
    firstNode = 1 if oneIndexed else 0
    size = firstNode + n
    if not firstNode <= source < size:
        raise ValueError(f"dijkstraUndirected: source {source} is outside the nodes {firstNode}..{size - 1}")
    adj = [[] for _ in range(size)]
    for a, b, w in edges:
        if not (firstNode <= a < size and firstNode <= b < size):
            raise ValueError(f"dijkstraUndirected: edge ({a}, {b}) is outside the nodes {firstNode}..{size - 1}")
        if w < 0:
            raise ValueError(f"dijkstraUndirected: edge ({a}, {b}) has negative weight {w}")
        adj[a].append((b, w))
        adj[b].append((a, w))
    dist = [None] * size
    prev = [None] * size
    dist[source] = 0
    heap = [(0, source)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue  # an older, longer entry for a node already settled
        for nxt, w in adj[node]:
            nd = d + w
            if dist[nxt] is None or nd < dist[nxt]:
                dist[nxt] = nd
                prev[nxt] = node
                heapq.heappush(heap, (nd, nxt))
    return dist, prev
