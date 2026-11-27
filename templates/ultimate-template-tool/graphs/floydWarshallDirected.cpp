// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallDirected.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// auto dist = floydWarshallDirected(numNodes, edges);
//   edges is a list of directed weighted edges {{from, to, weight}, ...}, weights >= 0
//   Repeated edges keep the cheapest; self-loops are ignored
//   numNodes is how many nodes there are: the nodes are 0..numNodes-1
//   (a node with no edges never shows up in edges, so numNodes has to be passed)
//   For example: floydWarshallDirected(4, {{0, 1, 4}, {0, 2, 1}, {2, 1, 2}})   (node 3 has no edges)
//
// dist[a][b] -> the shortest distance from a to b, e.g. dist[0] = {0, 3, 1, INF}
//   INF if b can't be reached from a, and 0 from a node to itself.
//   Here 0 -> 1 costs 3 by going through 2, instead of 4 directly
//   dist is a numNodes x numNodes matrix
//
// INF -> LLONG_MAX / 4, set at the top of the file: change it there if you need to
//
// O(V^3 + E) time, O(V^2) space. Negative weights throw invalid_argument
// (a loop with negative total weight would make distances meaningless)

const ll INF = LLONG_MAX / 4;  // what unreachable pairs hold (/ 4 so adding two distances can't overflow)

vector<vector<ll>> floydWarshallDirected(int numNodes, const vector<array<ll, 3>>& edges) {
    int size = numNodes;
    vector<vector<ll>> dist(size, vector<ll>(size, INF));
    for (int node = 0; node < size; node++) dist[node][node] = 0;
    for (auto [a, b, w] : edges) {
        if (a < 0 || a >= size || b < 0 || b >= size)
            throw out_of_range("floydWarshallDirected: an edge is outside the nodes 0..numNodes - 1");
        if (w < 0) throw invalid_argument("floydWarshallDirected: negative edge weight");
        dist[a][b] = min(dist[a][b], w);
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
