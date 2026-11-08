# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/SumOfDistances.py

# For every node, the sum of its distances (by edge count) to all other nodes
# edges = [[a, b], [c, d], ...]: an unrooted tree with at least 2 nodes
# labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
#   0-indexed -> length n
#   1-indexed -> length n + 1, index 0 is an unused dummy holding -1
# res = sumOfDistances([[0, 1], [1, 2], [1, 3]])
#   res = [5, 3, 5, 5]   res[i] = sum of distances from i to every other node
# O(n) time and space, iterative (no recursion limit issues)
def sumOfDistances(edges):
    size = max(max(a, b) for a, b in edges) + 1
    adj = [[] for _ in range(size)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    root = edges[0][0]
    parent = [-1] * size
    order = [root]
    for cur in order:
        par = parent[cur]
        for nxt in adj[cur]:
            if nxt != par:
                parent[nxt] = cur
                order.append(nxt)

    n = len(edges) + 1
    subSize = [1] * size
    down = [0] * size  # sum of distances from a node into its own subtree
    for i in range(len(order) - 1, 0, -1):
        cur = order[i]
        par = parent[cur]
        subSize[par] += subSize[cur]
        down[par] += down[cur] + subSize[cur]

    # moving from the parent to cur: cur's subtree gets 1 closer, everything else 1 farther
    res = [-1] * size
    res[root] = down[root]
    for i in range(1, len(order)):
        cur = order[i]
        res[cur] = res[parent[cur]] + n - 2 * subSize[cur]
    return res
