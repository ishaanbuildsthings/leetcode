// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/dijkstraDirected.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// auto [dist, prev] = dijkstraDirected(edges, n, oneIndexed, source);
//   edges is a list of directed weighted edges {{from, to, weight}, ...}, weights >= 0
//   n is how many nodes there are: the nodes are 0..n-1, or 1..n when oneIndexed is true
//   (a node with no edges never shows up in edges, so n has to be passed)
//   source is the node every distance is measured from
//   For example: dijkstraDirected({{1, 2, 4}, {1, 3, 1}, {3, 2, 2}, {2, 4, 5}}, 4, true, 1)
//
// dist -> the shortest distance from source to every node, e.g. {-1, 0, 3, 1, 8}
//   dist[node] is -1 if node can't be reached from source. With oneIndexed, dist[0] isn't a
//   node and is always -1. Here the best route to 4 costs 8
//
// prev -> the node right before each node on a shortest route from source, e.g. {-1, -1, 3, 1, 2}
//   Only needed to rebuild the route itself: start at the target and keep stepping to prev until
//   you reach source, then reverse. Here the route to 4 is 1 -> 3 -> 2 -> 4.
//   -1 for source itself and for nodes that can't be reached
//
// O((V + E) log E) time, O(V + E) space. Negative weights throw invalid_argument
pair<vector<ll>, vector<int>> dijkstraDirected(const vector<array<ll, 3>>& edges, int n, bool oneIndexed,
                                               int source) {
    int firstNode = oneIndexed ? 1 : 0, size = firstNode + n;
    if (source < firstNode || source >= size) throw out_of_range("dijkstraDirected: source is outside the nodes");
    vector<vector<pair<int, ll>>> adj(size);
    for (auto [a, b, w] : edges) {
        if (a < firstNode || a >= size || b < firstNode || b >= size)
            throw out_of_range("dijkstraDirected: an edge is outside the nodes 0..n-1 (or 1..n)");
        if (w < 0) throw invalid_argument("dijkstraDirected: negative edge weight");
        adj[a].push_back({b, w});
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
