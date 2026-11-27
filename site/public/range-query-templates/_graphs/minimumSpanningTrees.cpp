// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/minimumSpanningTrees.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// vector<vector<array<ll, 3>>> trees = minimumSpanningTrees(edges);
//   edges is a list of undirected weighted edges {{node1, node2, weight}, ...}; negative
//   weights, repeated edges and self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   For example: minimumSpanningTrees({{1, 2, 2}, {2, 3, 2}, {1, 3, 3}, {3, 4, 1}})
//
// trees -> one minimum spanning tree for each separate piece of the graph, e.g. {{{3, 4, 1}, {1, 2, 2}, {2, 3, 2}}}
//   Each tree is a list of its edges, cheapest first, written exactly as you gave them. A connected
//   graph has one piece, so you get a list holding one tree: use trees[0]. Adding up a tree's
//   weights gives its total, here 5
//
//   minimumSpanningTrees({{1, 2, 5}, {3, 4, 1}}) -> {{{1, 2, 5}}, {{3, 4, 1}}}
//   1 - 2 and 3 - 4 aren't connected, so that's two trees. Trees are ordered by their smallest
//   node, and a node with no edges has no tree
//
//   What each tree minimizes:
//   - the total weight, over every way of picking edges that connects all the nodes of its piece
//   - the biggest edge you have to cross between any two nodes: the path through the tree has the
//     smallest possible biggest edge of any path between them in the whole graph. Here 1 to 3
//     through the tree crosses edges of weight 2 and 2, while the direct edge weighs 3
//
//   What it does NOT minimize: the distance between two nodes. 1 to 3 through the tree costs
//   2 + 2 = 4, but the direct edge costs 3. For distances use Dijkstra or Floyd-Warshall
//
//   If several trees tie for cheapest, you get one of them
//
// O(E log E) time, O(V + E) space, V = number of nodes, E = number of edges

vector<vector<array<ll, 3>>> minimumSpanningTrees(const vector<array<ll, 3>>& edges) {
    ll size = 0;
    for (auto& [node1, node2, w] : edges) {
        if (node1 < 0 || node2 < 0) throw invalid_argument("minimumSpanningTrees: an edge has a negative label");
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

    // split the chosen edges by which piece of the graph they're in; pieces ordered by their smallest node
    vector<int> slot(size, -1);
    vector<ll> smallest;
    vector<vector<array<ll, 3>>> trees;
    for (auto& edge : tree) {
        int root = find(edge[0]);
        if (slot[root] == -1) {
            slot[root] = trees.size();
            trees.emplace_back();
            smallest.push_back(edge[0]);
        }
        trees[slot[root]].push_back(edge);  // stays cheapest first
        smallest[slot[root]] = min({smallest[slot[root]], edge[0], edge[1]});
    }
    vector<int> treeOrder(trees.size());
    iota(treeOrder.begin(), treeOrder.end(), 0);
    sort(treeOrder.begin(), treeOrder.end(), [&](int i, int j) { return smallest[i] < smallest[j]; });
    vector<vector<array<ll, 3>>> result;
    for (int i : treeOrder) result.push_back(move(trees[i]));
    return result;
}
