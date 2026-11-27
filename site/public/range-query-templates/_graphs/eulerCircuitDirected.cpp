// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerCircuitDirected.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<int> walk = eulerCircuitDirected(edges, start);   // start optional (-1 = not given)
//   edges is a list of directed edges {{from, to}, ...}; repeated edges and self-loops are fine
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   start is optional: the node the circuit has to start and end at. Left out, any node with edges
//   For example: eulerCircuitDirected({{1, 2}, {2, 3}, {3, 1}})
//
// walk -> the nodes in walking order, using every edge exactly once, e.g. {1, 2, 3, 1}
//   It has edges.size() + 1 nodes, and the first and last are the same node
//
//   {} if there's no circuit: some node has more edges in than out (or out than in), some edge can't be reached
//   from the start, or the start you gave has no edges
//   With no edges at all: just the start if you gave one, else {}
//
//   eulerCircuitDirected({{1, 2}, {2, 3}, {3, 1}}, 2) -> {2, 3, 1, 2}
//   eulerCircuitDirected({{1, 2}, {2, 3}}) -> {}
//
// O(V + E) time and space, V = number of nodes, E = number of edges
vector<int> eulerCircuitDirected(const vector<pair<int, int>>& edges, int start = -1) {
    if (edges.empty()) return start == -1 ? vector<int>{} : vector<int>{start};
    int size = start + 1;
    for (auto& [a, b] : edges) size = max({size, a + 1, b + 1});
    vector<vector<int>> adj(size);
    vector<int> balance(size, 0);  // out-degree minus in-degree
    for (auto& [a, b] : edges) {
        adj[a].push_back(b);
        balance[a]++;
        balance[b]--;
    }
    for (int node = 0; node < size; node++) {
        if (balance[node]) return {};
    }
    if (start == -1) start = edges[0].first;
    if (adj[start].empty()) return {};
    vector<int> stk = {start};
    vector<int> walk;
    walk.reserve(edges.size() + 1);
    while (!stk.empty()) {
        int node = stk.back();
        if (!adj[node].empty()) {
            stk.push_back(adj[node].back());
            adj[node].pop_back();
        } else {
            walk.push_back(node);
            stk.pop_back();
        }
    }
    if (walk.size() != edges.size() + 1) return {};
    reverse(walk.begin(), walk.end());
    return walk;
}
