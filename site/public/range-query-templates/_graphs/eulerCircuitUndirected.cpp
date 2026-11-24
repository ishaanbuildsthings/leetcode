// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitUndirected.cpp
#include <bits/stdc++.h>
using namespace std;

// Euler circuit on an undirected graph: a walk that uses every edge exactly once and ends where it started.
// edges: {{a, b}, ...}, labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated edges and
// self-loops are fine.
// start (optional, -1 = not given): the node the circuit must start and end at; any node with edges if left out.
// Returns the nodes in walk order (edges.size() + 1 of them, first == last), or {} if no circuit exists (some node
// has odd degree, edges not all reachable from the start, or a start that has no edges).
// No edges: {start} if a start was given, else {}.
// eulerCircuitUndirected({{1, 2}, {2, 3}, {3, 1}}) -> {1, 3, 2, 1}
// eulerCircuitUndirected({{1, 2}, {2, 3}, {3, 1}}, 2) -> {2, 3, 1, 2}
// eulerCircuitUndirected({{1, 2}, {2, 3}}) -> {}
// O(V + E) time and space, V = largest label, E = number of edges
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
