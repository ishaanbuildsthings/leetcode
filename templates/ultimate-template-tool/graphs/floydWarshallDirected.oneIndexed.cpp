// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/graphs/floydWarshallDirected.oneIndexed.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// auto dist = floydWarshallDirected(numNodes, edges);
//   edges is a list of directed weighted edges {{from, to, weight}, ...}, weights >= 0
//   Repeated edges keep the cheapest; self-loops are ignored
//   numNodes is how many nodes there are (it has to be passed since a node with no edges never shows up otherwise)
//   For example: floydWarshallDirected(4, {{1, 2, 4}, {1, 3, 1}, {3, 2, 2}})   (node 4 has no edges)
//
// dist[a][b] -> the shortest distance from a to b, e.g. dist[1] = {INF, 0, 3, 1, INF}
//   INF if b can't be reached from a, and 0 from a node to itself.
//   Here 1 -> 2 costs 3 by going through 3, instead of 4 directly
//   dist is a (numNodes + 1) x (numNodes + 1) matrix: node 0 doesn't exist, so row 0 and
//   column 0 are unused (all INF)
//
// INF -> LLONG_MAX / 4, set at the top of the file: change it there if you need to
//
// O(V^3 + E) time, O(V^2) space. Negative weights throw invalid_argument
// (a loop with negative total weight would make distances meaningless)

const ll INF = LLONG_MAX / 4;  // what unreachable pairs hold (/ 4 so adding two distances can't overflow)

vector<vector<ll>> floydWarshallDirected(int numNodes, const vector<array<ll, 3>>& edges) {
    int size = numNodes + 1;
    vector<vector<ll>> dist(size, vector<ll>(size, INF));
    for (int node = 1; node < size; node++) dist[node][node] = 0;
    for (auto [a, b, w] : edges) {
        if (a < 1 || a >= size || b < 1 || b >= size)
            throw out_of_range("floydWarshallDirected: an edge is outside the nodes 1..numNodes");
        if (w < 0) throw invalid_argument("floydWarshallDirected: negative edge weight");
        dist[a][b] = min(dist[a][b], w);
    }
    // allow each node in turn as a stopover: a -> mid -> b replaces a -> b when it's cheaper
    for (int mid = 1; mid < size; mid++) {
        const vector<ll>& midRow = dist[mid];
        for (int a = 1; a < size; a++) {
            ll toMid = dist[a][mid];
            if (toMid == INF) continue;
            vector<ll>& row = dist[a];
            for (int b = 1; b < size; b++) row[b] = min(row[b], toMid + midRow[b]);
        }
    }
    return dist;
}
