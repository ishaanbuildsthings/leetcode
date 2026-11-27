// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/topoSort.cpp
#include <bits/stdc++.h>
using namespace std;

// vector<int> order = topoSort(edges, n, oneIndexed);
//   edges is a list of directed edges {{from, to}, ...}, meaning from has to come before to
//   n is how many nodes there are: the nodes are 0..n-1, or 1..n when oneIndexed is true
//   (a node with no edges never shows up in edges, but it still has to be in the order)
//   For example: topoSort({{1, 3}, {2, 3}, {3, 4}}, 4, true)
//
// order -> every node exactly once, with from before to for every edge, e.g. {1, 2, 3, 4}
//   Nodes with nothing pointing to them come first, like an order you could take courses in.
//   Reverse it if you want everything a node points to to come first
//
//   {} if the graph has a cycle, since then no order works. So this is also the
//   "is it a DAG?" check: isDag = !topoSort(edges, n, oneIndexed).empty()  (for n >= 1)
//
// O(V + E) time and space
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
