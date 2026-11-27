// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/minimumSpanningTree.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// vector<array<ll, 3>> tree = minimumSpanningTree(edges);
//   edges is a list of undirected weighted edges {{node1, node2, weight}, ...}; negative
//   weights, repeated edges and self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   (a node with no edges can't be in the tree, so how many nodes there are doesn't matter)
//   For example: minimumSpanningTree({{1, 2, 2}, {2, 3, 2}, {1, 3, 3}, {3, 4, 1}})
//
// tree -> the edges of a minimum spanning tree, cheapest first, e.g. {{3, 4, 1}, {1, 2, 2}, {2, 3, 2}}
//   Each edge is written exactly as you gave it. Adding up the weights gives the tree's total
//   weight, here 5
//
//   What it minimizes:
//   - the total weight, over every way of picking edges that connects all the nodes
//   - the biggest edge you have to cross between any two nodes: the path through the tree has the
//     smallest possible biggest edge of any path between them in the whole graph. Here 1 to 3
//     through the tree crosses edges of weight 2 and 2, while the direct edge weighs 3
//
//   What it does NOT minimize: the distance between two nodes. 1 to 3 through the tree costs
//   2 + 2 = 4, but the direct edge costs 3. For distances use Dijkstra or Floyd-Warshall
//
//   If several trees tie for cheapest, you get one of them
//
//   If the graph isn't connected, there's no single tree, so you still get one flat list, holding
//   the cheapest tree for each separate piece mixed together: minimumSpanningTree({{1, 2, 5}, {3, 4, 1}})
//   -> {{3, 4, 1}, {1, 2, 5}}, which is two trees, 1 - 2 and 3 - 4. If your graph has V nodes, it's
//   connected exactly when the list has V - 1 edges
//
// O(E log E) time, O(V + E) space, V = largest label, E = number of edges

vector<array<ll, 3>> minimumSpanningTree(const vector<array<ll, 3>>& edges) {
    ll size = 0;
    for (auto& [node1, node2, w] : edges) {
        if (node1 < 0 || node2 < 0) throw invalid_argument("minimumSpanningTree: an edge has a negative label");
        size = max({size, node1 + 1, node2 + 1});
    }
    vector<int> parent(size);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int node) {
        while (parent[node] != node) {
            parent[node] = parent[parent[node]];
            node = parent[node];
        }
        return node;
    };
    // Kruskal: take edges cheapest first, keeping each one that joins two pieces not yet connected
    vector<int> order(edges.size());
    iota(order.begin(), order.end(), 0);
    stable_sort(order.begin(), order.end(), [&](int i, int j) { return edges[i][2] < edges[j][2]; });
    vector<array<ll, 3>> tree;
    for (int i : order) {
        int root1 = find(edges[i][0]), root2 = find(edges[i][1]);
        if (root1 != root2) {
            parent[root1] = root2;
            tree.push_back(edges[i]);
        }
    }
    return tree;
}
