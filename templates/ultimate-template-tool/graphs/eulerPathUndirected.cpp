// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathUndirected.cpp
#include <bits/stdc++.h>
using namespace std;

// Euler path on an undirected graph: a walk that uses every edge exactly once. It may end where it started (a circuit
// counts as a path).
// edges: {{a, b}, ...}, labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated edges and
// self-loops are fine.
// start, end (optional, -1 = not given): the nodes the path must start / end at. Left out, they're picked for you:
// with two odd-degree nodes the path runs between them (smaller label first); with none it's a circuit from any node
// with edges.
// Returns the nodes in walk order (edges.size() + 1 of them), or {} if no such path exists (degrees don't allow one,
// edges not all reachable from the start, or a start / end that doesn't fit).
// No edges: {start} or {end} if one was given ({} if both were given and differ), else {}.
// eulerPathUndirected({{1, 2}, {2, 3}, {3, 1}, {1, 4}}) -> {1, 3, 2, 1, 4}
// eulerPathUndirected({{1, 2}, {2, 3}}, 3) -> {3, 2, 1}
// eulerPathUndirected({{1, 2}, {1, 3}, {1, 4}}) -> {}
// O(N + M) time and space, N = largest label, M = number of edges
vector<int> eulerPathUndirected(const vector<pair<int, int>>& edges, int start = -1, int end = -1) {
    if (edges.empty()) {
        if (start != -1 && end != -1 && start != end) return {};
        if (start != -1) return {start};
        return end == -1 ? vector<int>{} : vector<int>{end};
    }
    int size = max(start, end) + 1;
    for (auto& [a, b] : edges) size = max({size, a + 1, b + 1});
    vector<vector<pair<int, int>>> adj(size);  // adj[node] = {neighbor, edge id}, each edge in both endpoints' lists
    for (int edgeId = 0; edgeId < (int)edges.size(); edgeId++) {
        auto [a, b] = edges[edgeId];
        adj[a].push_back({b, edgeId});
        adj[b].push_back({a, edgeId});
    }
    vector<int> odd;
    for (int node = 0; node < size; node++) {
        if (adj[node].size() % 2) odd.push_back(node);
    }
    if (odd.size() != 0 && odd.size() != 2) return {};
    if (!odd.empty()) {
        for (int node : {start, end}) {
            if (node != -1 && node != odd[0] && node != odd[1]) return {};
        }
        if (start != -1 && start == end) return {};
        if (start == -1) start = end == odd[0] ? odd[1] : odd[0];
    } else {
        if (start != -1 && end != -1 && start != end) return {};
        if (start == -1) start = end != -1 ? end : edges[0].first;
        if (adj[start].empty()) return {};
    }
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
