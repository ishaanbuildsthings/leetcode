# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/hasCycleDirected.py

# hasCycle = hasCycleDirected(edges)
#   edges is a list of directed edges [[from, to], ...]
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   (a node with no edges can't be on a cycle, so how many nodes there are doesn't matter)
#   For example: hasCycleDirected([[1, 2], [2, 3], [3, 1]])
#
# hasCycle -> True if you can start at some node, follow edges, and get back to it, e.g. True
#   A self-loop counts as a cycle. 1 -> 2 with 2 -> 1 is a cycle, but 1 -> 2, 1 -> 3, 2 -> 3 is not,
#   since you can't get back to where you started
#
#   hasCycleDirected([[1, 2], [1, 3], [2, 3]]) -> False
#   hasCycleDirected([[1, 2], [2, 1]]) -> True
#
# O(V + E) time and space, V = largest label, E = number of edges


def hasCycleDirected(edges):
    size = 0
    for a, b in edges:
        if a < 0 or b < 0:
            raise ValueError(f"hasCycleDirected: edge ({a}, {b}) has a negative label")
        size = max(size, a + 1, b + 1)
    adj = [[] for _ in range(size)]
    inDegree = [0] * size
    for a, b in edges:
        adj[a].append(b)
        inDegree[b] += 1
    # keep removing nodes nothing points to; if some never get removed, they sit on or behind a cycle
    stack = [node for node in range(size) if inDegree[node] == 0]
    removed = 0
    while stack:
        node = stack.pop()
        removed += 1
        for nxt in adj[node]:
            inDegree[nxt] -= 1
            if inDegree[nxt] == 0:
                stack.append(nxt)
    return removed != size
