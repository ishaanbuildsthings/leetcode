// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/hasCycleDirected.cpp
#include <bits/stdc++.h>
using namespace std;

// bool hasCycle = hasCycleDirected(edges);
//   edges is a list of directed edges {{from, to}, ...}
//   The nodes are 0..n-1 or 1..n, sized from the largest label, so nothing else has to be passed
//   (a node with no edges can't be on a cycle, so how many nodes there are doesn't matter)
//   For example: hasCycleDirected({{1, 2}, {2, 3}, {3, 1}})
//
// hasCycle -> true if you can start at some node, follow edges, and get back to it, e.g. true
//   A self-loop counts as a cycle. 1 -> 2 with 2 -> 1 is a cycle, but 1 -> 2, 1 -> 3, 2 -> 3 is not,
//   since you can't get back to where you started
//
//   hasCycleDirected({{1, 2}, {1, 3}, {2, 3}}) -> false
//   hasCycleDirected({{1, 2}, {2, 1}}) -> true
//
// O(V + E) time and space, V = largest label, E = number of edges

bool hasCycleDirected(const vector<pair<int, int>>& edges) {
    int size = 0;
    for (auto [a, b] : edges) {
        if (a < 0 || b < 0) throw invalid_argument("hasCycleDirected: an edge has a negative label");
        size = max({size, a + 1, b + 1});
    }
    vector<vector<int>> adj(size);
    vector<int> inDegree(size, 0);
    for (auto [a, b] : edges) {
        adj[a].push_back(b);
        inDegree[b]++;
    }
    // keep removing nodes nothing points to; if some never get removed, they sit on or behind a cycle
    vector<int> stack;
    for (int node = 0; node < size; node++)
        if (inDegree[node] == 0) stack.push_back(node);
    int removed = 0;
    while (!stack.empty()) {
        int node = stack.back();
        stack.pop_back();
        removed++;
        for (int nxt : adj[node])
            if (--inDegree[nxt] == 0) stack.push_back(nxt);
    }
    return removed != size;
}
