# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/dijkstraUndirected.py

# dist, prev = dijkstraUndirected(edges, numNodes, oneIndexed, source)
#   edges is a list of undirected weighted edges [[node1, node2, weight], ...], usable both ways, weights >= 0
#   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
#   oneIndexed is True when the nodes are 1..numNodes, False when they're 0..numNodes-1
#   source is the node every distance is measured from
#   For example: dijkstraUndirected([[1, 2, 4], [1, 3, 1], [3, 2, 2], [2, 4, 5]], 4, True, 1)
#
# dist -> the shortest distance from source to every node, e.g. [None, 0, 3, 1, 8]
#   dist[node] is None if node can't be reached from source. With oneIndexed, dist[0] isn't a
#   node and is always None. Here the best route to 4 costs 8
#
# prev -> the node right before each node on a shortest route from source, e.g. [None, None, 3, 1, 2]
#   Only needed to rebuild the route itself: start at the target and keep stepping to prev until
#   you reach source, then reverse. Here the route to 4 is 1 -> 3 -> 2 -> 4.
#   None for source itself and for nodes that can't be reached
#
# O((V + E) log E) time, O(V + E) space. Negative weights raise ValueError
import heapq


def dijkstraUndirected(edges, numNodes, oneIndexed: bool, source):
    firstNode = 1 if oneIndexed else 0
    size = firstNode + numNodes
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
