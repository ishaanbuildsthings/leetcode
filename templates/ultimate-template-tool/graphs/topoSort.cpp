// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/topoSort.cpp
#include <bits/stdc++.h>
using namespace std;

// Topological sort of a directed graph (Kahn's algorithm), which doubles as the "is it a DAG?" check.
// edges: {{a, b}, ...} meaning a -> b ("a must come before b", e.g. a is a prerequisite of b); repeated edges are
// fine, a self-loop is a cycle.
// n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is true. A node with no edges never
// shows up in the edge list but still has to appear in the order. Every edge must stay in that range, else
// out_of_range.
// Returns {} if the graph has a cycle (not a DAG). Otherwise every node exactly once, ordered so that for every edge
// a -> b, a comes BEFORE b: nodes with no incoming edges come first, the order you could take courses in. Reverse it
// for "everything a node points to comes first". (n = 0 also gives {}: no nodes, nothing to order.)
//   topoSort({{1, 3}, {2, 3}}, 3, true)          -> {1, 2, 3}
//   topoSort({{0, 1}}, 3, false)                 -> {0, 2, 1}     (node 2 has no edges)
//   topoSort({{1, 2}, {2, 3}, {3, 1}}, 3, true)  -> {}            (cycle)
//   bool isDag = (int)topoSort(edges, n, oneIndexed).size() == n;
// O(V + E) time and space, V = n, E = number of edges
vector<int> topoSort(const vector<pair<int, int>>& edges, int n, bool oneIndexed) {
    if (n < 0) throw invalid_argument("topoSort: needs n >= 0");
    int firstNode = oneIndexed ? 1 : 0, lastNode = firstNode + n - 1;
    int size = lastNode + 1;
    vector<vector<int>> adj(size);
    vector<int> inDegree(size, 0);
    for (auto [a, b] : edges) {
        if (a < firstNode || a > lastNode || b < firstNode || b > lastNode)
            throw out_of_range("topoSort: an edge is outside the nodes 0..n-1 (or 1..n)");
        adj[a].push_back(b);
        inDegree[b]++;
    }
    vector<int> order;
    order.reserve(n);
    for (int node = firstNode; node < size; node++) {
        if (!inDegree[node]) order.push_back(node);
    }
    for (int i = 0; i < (int)order.size(); i++) {
        int node1 = order[i];
        for (int node2 : adj[node1]) {
            if (!--inDegree[node2]) order.push_back(node2);
        }
    }
    if ((int)order.size() != n) return {};
    return order;
}
