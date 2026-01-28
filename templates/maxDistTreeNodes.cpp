
#include <bits/stdc++.h>
using namespace std;
// ⚠️ Not optimized
// O(n) time to get the maximum distance + max distance node, for all nodes
// ✅ Passed on https://codeforces.com/contest/1822/submission/360265085

// Input: edges of a tree (n-1 edges).
// - Node labels may be 0..n-1 or 1..n (auto-detected).
// Output:
//   maxDist[i] = eccentricity of node i (max distance in edges)
//   farNode[i] = a node achieving that distance
//
// Returns vectors sized to the max label + 1; entries for unused label 0/1 will exist if the other convention is used.
pair<vector<int>, vector<int>> farthestInfoPerNode(const vector<pair<int,int>>& edges) {
    if (edges.empty()) return {{}, {}};

    int mn = INT_MAX, mx = INT_MIN;
    for (auto [a, b] : edges) {
        mn = min(mn, min(a, b));
        mx = max(mx, max(a, b));
    }

    bool oneBased = (mn == 1); // typical CF trees
    int n = oneBased ? mx : (mx + 1); // nodes are 1..n or 0..n-1
    int base = oneBased ? 1 : 0;
    int root = base;

    int N = oneBased ? (n + 1) : n;
    vector<vector<int>> adj(N);
    for (auto [a, b] : edges) {
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    vector<int> downBest(N, 0), downNode(N, -1);
    vector<pair<int,int>> top1(N, {0, -1}), top2(N, {0, -1});
    vector<int> upBest(N, 0), upNode(N, -1);

    auto dfs1 = [&](auto&& self, int u, int p) -> void {
        downNode[u] = u;
        top1[u] = {0, u};
        top2[u] = {0, u};

        for (int v : adj[u]) {
            if (v == p) continue;
            self(self, v, u);

            int candDist = 1 + downBest[v];
            int candNode = downNode[v];

            if (candDist > top1[u].first) {
                top2[u] = top1[u];
                top1[u] = {candDist, candNode};
            } else if (candDist > top2[u].first) {
                top2[u] = {candDist, candNode};
            }
        }

        downBest[u] = top1[u].first;
        downNode[u] = top1[u].second;
    };

    dfs1(dfs1, root, -1);

    upBest[root] = 0;
    upNode[root] = root;

    auto dfs2 = [&](auto&& self, int u, int p) -> void {
        for (int v : adj[u]) {
            if (v == p) continue;

            pair<int,int> bestExclV = top1[u];
            if (bestExclV.first == 1 + downBest[v] && bestExclV.second == downNode[v]) {
                bestExclV = top2[u];
            }

            int cand1Dist = 1 + bestExclV.first;
            int cand1Node = bestExclV.second;

            int cand2Dist = 1 + upBest[u];
            int cand2Node = upNode[u];

            if (cand1Dist >= cand2Dist) {
                upBest[v] = cand1Dist;
                upNode[v] = cand1Node;
            } else {
                upBest[v] = cand2Dist;
                upNode[v] = cand2Node;
            }

            self(self, v, u);
        }
    };

    dfs2(dfs2, root, -1);

    vector<int> maxDist(N, 0), farNode(N, -1);
    for (int u = base; u < base + n; u++) {
        if (downBest[u] >= upBest[u]) {
            maxDist[u] = downBest[u];
            farNode[u] = downNode[u];
        } else {
            maxDist[u] = upBest[u];
            farNode[u] = upNode[u];
        }
    }

    return {maxDist, farNode};
}
