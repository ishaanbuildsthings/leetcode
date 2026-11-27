# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/undirectedComponents.py

# components = undirectedComponents(edges, numNodes, oneIndexed)
#   edges is a list of undirected edges [[node1, node2], ...]; repeated edges and self-loops are fine
#   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
#   oneIndexed is True when the nodes are 1..numNodes, False when they're 0..numNodes-1
#   For example: undirectedComponents([[1, 2], [2, 3], [4, 5]], 6, True)   (node 6 has no edges)
#
# components -> one (nodes, edgeList) per component, e.g.
#   [([1, 2, 3], [[1, 2], [2, 3]]), ([4, 5], [[4, 5]]), ([6], [])]
#   nodes are increasing, and edgeList is that component's edges in the order you gave them.
#   A node with no edges is a component by itself, with no edges
#
#   Components are ordered by their smallest node, and len(components) is how many there are
#
# O((V + E) α(V)) time (union-find, so practically linear), O(V + E) space


def undirectedComponents(edges, numNodes, oneIndexed: bool):
    firstNode = 1 if oneIndexed else 0
    size = firstNode + numNodes
    parent = list(range(size))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    for a, b in edges:
        if not (firstNode <= a < size and firstNode <= b < size):
            raise ValueError(f"undirectedComponents: edge ({a}, {b}) is outside the nodes {firstNode}..{size - 1}")
        rootA, rootB = find(a), find(b)
        if rootA != rootB:
            parent[rootA] = rootB

    # components ordered by their smallest node, nodes increasing, edges in the order given
    slot = [-1] * size  # slot[root] = where that root's component sits in components
    components = []
    for node in range(firstNode, size):
        root = find(node)
        if slot[root] == -1:
            slot[root] = len(components)
            components.append(([], []))
        components[slot[root]][0].append(node)
    for a, b in edges:
        components[slot[find(a)]][1].append([a, b])
    return components
