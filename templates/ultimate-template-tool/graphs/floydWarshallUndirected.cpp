// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallUndirected.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// Floyd-Warshall, undirected graph, 0-indexed: shortest distance between every pair of nodes.
// numNodes: how many nodes there are; the nodes are 0..numNodes - 1. (A node with no edges never shows up
// in the edge list, so the count has to be passed.)
// edges: [a, b, w] meaning a <-> b, usable both ways, with weight w >= 0. Repeated edges keep the cheapest; self-loops
// are ignored. A negative weight is an error (a negative loop would make some distances meaningless).
// Returns dist, a numNodes x numNodes matrix: dist[a][b] = the shortest distance from a to b, INF if b
// can't be reached from a, 0 for a to itself.
// Example:
//   auto dist = floydWarshallUndirected(4, {{0, 1, 4}, {0, 2, 1}, {2, 1, 2}});
//   dist[0] -> {0, 3, 1, INF}    0 -> 1 costs 3 (through 2); node 3 has no edges, so it's INF
//   dist[1] -> {3, 0, 2, INF}
// O(V^3 + E) time, O(V^2) space, V = numNodes, E = number of edges. Negative weights throw invalid_argument.

const ll INF = LLONG_MAX / 4;  // what unreachable pairs hold (/ 4 so adding two distances can't overflow)

vector<vector<ll>> floydWarshallUndirected(int numNodes, const vector<array<ll, 3>>& edges) {
    int size = numNodes;
    vector<vector<ll>> dist(size, vector<ll>(size, INF));
    for (int node = 0; node < size; node++) dist[node][node] = 0;
    for (auto [a, b, w] : edges) {
        if (a < 0 || a >= size || b < 0 || b >= size)
            throw out_of_range("floydWarshallUndirected: an edge is outside the nodes 0..numNodes - 1");
        if (w < 0) throw invalid_argument("floydWarshallUndirected: negative edge weight");
        dist[a][b] = min(dist[a][b], w);
        dist[b][a] = min(dist[b][a], w);
    }
    // allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper
    for (int mid = 0; mid < size; mid++) {
        const vector<ll>& midRow = dist[mid];
        for (int a = 0; a < size; a++) {
            ll toMid = dist[a][mid];
            if (toMid == INF) continue;
            vector<ll>& row = dist[a];
            for (int b = 0; b < size; b++) row[b] = min(row[b], toMid + midRow[b]);
        }
    }
    return dist;
}
