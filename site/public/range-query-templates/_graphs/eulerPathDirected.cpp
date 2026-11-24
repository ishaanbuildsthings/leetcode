// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/eulerPathDirected.cpp
#include <bits/stdc++.h>
using namespace std;

// Euler path on a directed graph: a walk that uses every edge exactly once. It may end where it started (a circuit
// counts as a path).
// edges: {{a, b}, ...} meaning a -> b, labels 0..n-1 or 1..n (sized to the largest label, nothing to pass); repeated
// edges and self-loops are fine.
// start, end (optional, -1 = not given): the nodes the path must start / end at. Left out, they're picked for you: the
// node with one more out than in starts and the node with one more in than out ends; if every node is balanced the
// path is a circuit from any node with edges.
// Returns the nodes in walk order (edges.size() + 1 of them), or {} if no such path exists (degrees don't allow one,
// edges not all reachable from the start, or a start / end that doesn't fit).
// No edges: {start} or {end} if one was given ({} if both were given and differ), else {}.
// eulerPathDirected({{1, 2}, {2, 3}, {3, 1}, {1, 4}}) -> {1, 2, 3, 1, 4}
// eulerPathDirected({{1, 2}, {2, 1}}, 2, 2) -> {2, 1, 2}
// eulerPathDirected({{1, 2}, {1, 3}}) -> {}
// O(N + M) time and space, N = largest label, M = number of edges
vector<int> eulerPathDirected(const vector<pair<int, int>>& edges, int start = -1, int end = -1) {
    if (edges.empty()) {
        if (start != -1 && end != -1 && start != end) return {};
        if (start != -1) return {start};
        return end == -1 ? vector<int>{} : vector<int>{end};
    }
    int size = max(start, end) + 1;
    for (auto& [a, b] : edges) size = max({size, a + 1, b + 1});
    vector<vector<int>> adj(size);
    vector<int> balance(size, 0);  // out-degree minus in-degree
    for (auto& [a, b] : edges) {
        adj[a].push_back(b);
        balance[a]++;
        balance[b]--;
    }
    int extraOut = -1, extraIn = -1;
    for (int node = 0; node < size; node++) {
        if (balance[node] == 0) continue;
        if (balance[node] == 1 && extraOut == -1) extraOut = node;
        else if (balance[node] == -1 && extraIn == -1) extraIn = node;
        else return {};  // off by 2 or more, or a second unbalanced node of the same kind
    }
    if ((extraOut == -1) != (extraIn == -1)) return {};
    if (extraOut != -1) {
        if (start != -1 && start != extraOut) return {};
        if (end != -1 && end != extraIn) return {};
        start = extraOut;
    } else {
        if (start != -1 && end != -1 && start != end) return {};
        if (start == -1) start = end != -1 ? end : edges[0].first;
        if (adj[start].empty()) return {};
    }
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
