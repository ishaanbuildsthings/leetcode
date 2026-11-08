# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/reroot/SumOfDistances.weighted.py

# For every node, the sum of its distances (by total edge weight) to all other nodes
# edges = [[a, b, w], [c, d, w], ...]: an unrooted tree with at least 2 nodes, any int weights
# labels can be 0..n-1 or 1..n, no flag needed: the output is sized to the largest label
#   0-indexed -> length n
#   1-indexed -> length n + 1, index 0 is an unused dummy holding -1
# res = sumOfDistances([[0, 1, 5], [1, 2, 3], [1, 3, 4]])
#   res = [22, 12, 18, 20]   res[i] = sum of distances from i to every other node
# O(n) time and space, iterative (no recursion limit issues)
def sumOfDistances(edges):
    size = max(max(a, b) for a, b, _ in edges) + 1
    adj = [[] for _ in range(size)]
    for a, b, w in edges:
        adj[a].append((b, w))
        adj[b].append((a, w))

    root = edges[0][0]
    parent = [-1] * size
    parentW = [0] * size
    order = [root]
    for cur in order:
        par = parent[cur]
        for nxt, w in adj[cur]:
            if nxt != par:
                parent[nxt] = cur
                parentW[nxt] = w
                order.append(nxt)

    n = len(edges) + 1
    subSize = [1] * size
    down = [0] * size  # sum of distances from a node into its own subtree
    for i in range(len(order) - 1, 0, -1):
        cur = order[i]
        par = parent[cur]
        subSize[par] += subSize[cur]
        down[par] += down[cur] + subSize[cur] * parentW[cur]

    # moving across an edge of weight w: cur's subtree gets w closer, everything else w farther
    res = [-1] * size
    res[root] = down[root]
    for i in range(1, len(order)):
        cur = order[i]
        res[cur] = res[parent[cur]] + parentW[cur] * (n - 2 * subSize[cur])
    return res
