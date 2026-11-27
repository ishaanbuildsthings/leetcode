// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/hasCycleUndirected.cpp
#include <bits/stdc++.h>
using namespace std;

// bool hasCycle = hasCycleUndirected(edges);
//   edges is a list of undirected edges {{node1, node2}, ...}
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   (a node with no edges can't be on a cycle, so how many nodes there are doesn't matter)
//   For example: hasCycleUndirected({{1, 2}, {2, 3}, {3, 1}})
//
// hasCycle -> true if there's a loop anywhere in the graph, e.g. true
//   A self-loop counts as a cycle, and so do two copies of the same edge, since you can go out
//   along one and come back along the other
//
//   hasCycleUndirected({{1, 2}, {2, 3}}) -> false
//   hasCycleUndirected({{1, 2}, {2, 1}}) -> true    (the same edge twice)
//
// O(V + E α(V)) time (union-find, so practically linear), O(V) space, V = largest label

bool hasCycleUndirected(const vector<pair<int, int>>& edges) {
    int size = 0;
    for (auto [a, b] : edges) {
        if (a < 0 || b < 0) throw invalid_argument("hasCycleUndirected: an edge has a negative label");
        size = max({size, a + 1, b + 1});
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
    // an edge between two nodes that are already connected closes a loop
    for (auto [a, b] : edges) {
        int rootA = find(a), rootB = find(b);
        if (rootA == rootB) return true;
        parent[rootA] = rootB;
    }
    return false;
}
