// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathUndirected.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<int> walk = eulerPathUndirected(edges, start, end);   // start, end optional (-1 = not given)
//   edges is a list of undirected edges {{from, to}, ...}; repeated edges and self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   start and end are optional: the nodes the walk has to start and end at. Left out, they're
//   picked for you: with two odd-degree nodes, the path runs from one to the other.
//   If every node has even degree, the walk is a circuit from any node with edges
//   For example: eulerPathUndirected({{1, 2}, {2, 3}, {3, 1}, {1, 4}})
//
// walk -> the nodes in walking order, using every edge exactly once, e.g. {1, 3, 2, 1, 4}
//   It has edges.size() + 1 nodes and may end where it started (a circuit counts)
//
//   {} if there's no such walk: the degrees don't allow one, some edge can't be reached
//   from the start, or the start / end you gave doesn't fit
//   With no edges at all: just the start or end if you gave one, else {}
//
//   eulerPathUndirected({{1, 2}, {2, 3}}, 3) -> {3, 2, 1}
//   eulerPathUndirected({{1, 2}, {1, 3}, {1, 4}}) -> {}
//
// O(V + E) time and space, V = largest label, E = number of edges
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
