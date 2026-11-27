// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/undirectedComponents.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<Component> components = undirectedComponents(edges, numNodes, oneIndexed);
//   edges is a list of undirected edges {{node1, node2}, ...}; repeated edges and self-loops are fine
//   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
//   oneIndexed is true when the nodes are 1..numNodes, false when they're 0..numNodes-1
//   For example: undirectedComponents({{1, 2}, {2, 3}, {4, 5}}, 6, true)   (node 6 has no edges)
//
// components -> one {nodes, edgeList} per component, e.g.
//   components[0].nodes -> {1, 2, 3}   components[0].edgeList -> {{1, 2}, {2, 3}}
//   components[1].nodes -> {4, 5}      components[1].edgeList -> {{4, 5}}
//   components[2].nodes -> {6}         components[2].edgeList -> {}
//   nodes are increasing, and edgeList is that component's edges in the order you gave them.
//   A node with no edges is a component by itself, with no edges
//
//   Components are ordered by their smallest node, and components.size() is how many there are
//
// O((V + E) α(V)) time (union-find, so practically linear), O(V + E) space

struct Component {
    vector<int> nodes;
    vector<pair<int, int>> edgeList;
};

vector<Component> undirectedComponents(const vector<pair<int, int>>& edges, int numNodes, bool oneIndexed) {
    int firstNode = oneIndexed ? 1 : 0, size = firstNode + numNodes;
    vector<int> parent(size);
    iota(parent.begin(), parent.end(), 0);
    auto find = [&](int node) {
        while (parent[node] != node) {
            parent[node] = parent[parent[node]];
            node = parent[node];
        }
        return node;
    };
    for (auto [a, b] : edges) {
        if (a < firstNode || a >= size || b < firstNode || b >= size)
            throw out_of_range("undirectedComponents: an edge is outside the nodes 0..numNodes-1 (or 1..numNodes)");
        int rootA = find(a), rootB = find(b);
        if (rootA != rootB) parent[rootA] = rootB;
    }

    // components ordered by their smallest node, nodes increasing, edges in the order given
    vector<int> slot(size, -1);  // slot[root] = where that root's component sits in components
    vector<Component> components;
    for (int node = firstNode; node < size; node++) {
        int root = find(node);
        if (slot[root] == -1) {
            slot[root] = components.size();
            components.emplace_back();
        }
        components[slot[root]].nodes.push_back(node);
    }
    for (auto [a, b] : edges) components[slot[find(a)]].edgeList.push_back({a, b});
    return components;
}
