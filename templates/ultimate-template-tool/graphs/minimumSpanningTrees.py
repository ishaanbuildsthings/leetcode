# Template by https://github.com/ishaanbuildsthings
# https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/minimumSpanningTrees.py

# trees = minimumSpanningTrees(edges)
#   edges is a list of undirected weighted edges [[node1, node2, weight], ...]; negative
#   weights, repeated edges and self-loops are fine
#   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
#   For example: minimumSpanningTrees([[1, 2, 2], [2, 3, 2], [1, 3, 3], [3, 4, 1]])
#
# trees -> one minimum spanning tree for each separate piece of the graph, e.g. [[[3, 4, 1], [1, 2, 2], [2, 3, 2]]]
#   Each tree is a list of its edges, cheapest first, written exactly as you gave them. A connected
#   graph has one piece, so you get a list holding one tree: use trees[0]. Adding up a tree's
#   weights gives its total, here 5
#
#   minimumSpanningTrees([[1, 2, 5], [3, 4, 1]]) -> [[[1, 2, 5]], [[3, 4, 1]]]
#   1 - 2 and 3 - 4 aren't connected, so that's two trees. Trees are ordered by their smallest
#   node, and a node with no edges has no tree
#
#   What each tree minimizes:
#   - the total weight, over every way of picking edges that connects all the nodes of its piece
#   - the biggest edge you have to cross between any two nodes: the path through the tree has the
#     smallest possible biggest edge of any path between them in the whole graph. Here 1 to 3
#     through the tree crosses edges of weight 2 and 2, while the direct edge weighs 3
#
#   What it does NOT minimize: the distance between two nodes. 1 to 3 through the tree costs
#   2 + 2 = 4, but the direct edge costs 3. For distances use Dijkstra or Floyd-Warshall
#
#   If several trees tie for cheapest, you get one of them
#
# O(E log E) time, O(V + E) space, V = number of nodes, E = number of edges


def minimumSpanningTrees(edges):
    size = 0
    for node1, node2, w in edges:
        if node1 < 0 or node2 < 0:
            raise ValueError(f"minimumSpanningTrees: edge ({node1}, {node2}) has a negative label")
        size = max(size, node1 + 1, node2 + 1)
    parent = list(range(size))

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    # Kruskal: take edges cheapest first, keeping each one that joins two pieces not yet connected
    tree = []
    for edge in sorted(edges, key=lambda e: e[2]):
        root1, root2 = find(edge[0]), find(edge[1])
        if root1 != root2:
            parent[root1] = root2
            tree.append(list(edge))

    # split the chosen edges by which piece of the graph they're in; pieces ordered by their smallest node
    trees = {}
    smallest = {}
    for edge in tree:
        root = find(edge[0])
        trees.setdefault(root, []).append(edge)  # stays cheapest first
        smallest[root] = min(smallest.get(root, edge[0]), edge[0], edge[1])
    return [trees[root] for root in sorted(trees, key=smallest.get)]
