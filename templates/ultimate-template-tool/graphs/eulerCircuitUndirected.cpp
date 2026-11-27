// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitUndirected.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<int> walk = eulerCircuitUndirected(edges, start);   // start optional (-1 = not given)
//   edges is a list of undirected edges {{node1, node2}, ...}; repeated edges and self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   start is optional: the node the circuit has to start and end at. Left out, any node with edges
//   For example: eulerCircuitUndirected({{1, 2}, {2, 3}, {3, 1}})
//
// walk -> the nodes in walking order, using every edge exactly once, e.g. {1, 3, 2, 1}
//   It has edges.size() + 1 nodes, and the first and last are the same node
//
//   {} if there's no circuit: some node has odd degree, some edge can't be reached
//   from the start, or the start you gave has no edges
//   With no edges at all: just the start if you gave one, else {}
//
//   eulerCircuitUndirected({{1, 2}, {2, 3}, {3, 1}}, 2) -> {2, 3, 1, 2}
//   eulerCircuitUndirected({{1, 2}, {2, 3}}) -> {}
//
// O(V + E) time and space, V = number of nodes, E = number of edges
vector<int> eulerCircuitUndirected(const vector<pair<int, int>>& edges, int start = -1) {
    if (edges.empty()) return start == -1 ? vector<int>{} : vector<int>{start};
    int size = start + 1;
    for (auto& [a, b] : edges) size = max({size, a + 1, b + 1});
    vector<vector<pair<int, int>>> adj(size);  // adj[node] = {neighbor, edge id}, each edge in both endpoints' lists
    for (int edgeId = 0; edgeId < (int)edges.size(); edgeId++) {
        auto [a, b] = edges[edgeId];
        adj[a].push_back({b, edgeId});
        adj[b].push_back({a, edgeId});
    }
    for (int node = 0; node < size; node++) {
        if (adj[node].size() % 2) return {};
    }
    if (start == -1) start = edges[0].first;
    if (adj[start].empty()) return {};
    vector<bool> used(edges.size(), false);
    vector<int> stk = {start};
    vector<int> walk;
    walk.reserve(edges.size() + 1);
    while (!stk.empty()) {
        int node = stk.back();
        while (!adj[node].empty() && used[adj[node].back().second]) {
            adj[node].pop_back();  // (the other copy of an edge already walked from its other end)
        }
        if (!adj[node].empty()) {
            auto [nxt, edgeId] = adj[node].back();
            adj[node].pop_back();
            used[edgeId] = true;
            stk.push_back(nxt);
        } else {
            walk.push_back(node);
            stk.pop_back();
        }
    }
    if (walk.size() != edges.size() + 1) return {};
    reverse(walk.begin(), walk.end());
    return walk;
}
