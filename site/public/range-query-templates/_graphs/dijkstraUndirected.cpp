// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/dijkstraUndirected.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Dijkstra, undirected graph: shortest distance from source to every node, plus the previous node on a shortest route.
// edges: {{a, b, w}, ...} meaning a <-> b (both ways) with weight w >= 0; repeated edges and self-loops are
// fine.
// n, oneIndexed (both required): the nodes are 0..n-1, or 1..n when oneIndexed is true. A node with no
// edges never shows up in the edge list, so n says how many there are; oneIndexed says where the labels start.
// Returns two lists, both indexed by your node labels:
//   dist[node]  the shortest distance from source to node; -1 if node can't be reached
//   prev[node]  the node a shortest route to node comes from, one step before it; -1 for the source itself and
//               for nodes that can't be reached
// With oneIndexed, index 0 isn't a node: dist[0] and prev[0] are just -1 placeholders, ignore them.
// To get the route itself, start at the target and keep stepping to prev until you reach the source (that walks it
// backwards).
// Example, 1-indexed: edges 1-2 (4), 1-3 (1), 3-2 (2), 2-4 (5), source 1
//   auto [dist, prev] = dijkstraUndirected({{1, 2, 4}, {1, 3, 1}, {3, 2, 2}, {2, 4, 5}}, 4, true, 1);
//   dist -> {-1, 0, 3, 1, 8}      dist[4] = 8: the best route to 4 costs 1 + 2 + 5
//   prev -> {-1, -1, 3, 1, 2}   prev[4] = 2, prev[2] = 3, prev[3] = 1: the route is 1 -> 3 -> 2 -> 4
// O((V + E) log E) time, O(V + E) space, V = n, E = number of edges. Negative weights throw invalid_argument.
pair<vector<ll>, vector<int>> dijkstraUndirected(const vector<array<ll, 3>>& edges, int n, bool oneIndexed,
                                                 int source) {
    int firstNode = oneIndexed ? 1 : 0, size = firstNode + n;
    if (source < firstNode || source >= size) throw out_of_range("dijkstraUndirected: source is outside the nodes");
    vector<vector<pair<int, ll>>> adj(size);
    for (auto [a, b, w] : edges) {
        if (a < firstNode || a >= size || b < firstNode || b >= size)
            throw out_of_range("dijkstraUndirected: an edge is outside the nodes 0..n-1 (or 1..n)");
        if (w < 0) throw invalid_argument("dijkstraUndirected: negative edge weight");
        adj[a].push_back({b, w});
        adj[b].push_back({a, w});
    }
    vector<ll> dist(size, -1);
    vector<int> prev(size, -1);
    priority_queue<pair<ll, int>, vector<pair<ll, int>>, greater<>> heap;
    dist[source] = 0;
    heap.push({0, source});
    while (!heap.empty()) {
        auto [d, node] = heap.top();
        heap.pop();
        if (d > dist[node]) continue;  // an older, longer entry for a node already settled
        for (auto [nxt, w] : adj[node]) {
            ll nd = d + w;
            if (dist[nxt] == -1 || nd < dist[nxt]) {
                dist[nxt] = nd;
                prev[nxt] = node;
                heap.push({nd, nxt});
            }
        }
    }
    return {dist, prev};
}
