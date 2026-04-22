#include<bits/stdc++.h>
using namespace std;

// Returns vector where res[i] = max distance from node i to any other node.
// Works with either 0-indexed nodes (in [0, n)) or 1-indexed nodes (in [1, n]).
// res has size n + 1; the unused slot (either res[0] or res[n], depending on your convention) is 0.
vector<int> treeMaxDistances(int n, const vector<pair<int,int>>& edges) {
    int sz = n + 1;
    vector<vector<int>> adj(sz);
    for (auto [a, b] : edges) {
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    vector<array<int, 2>> down2(sz, {0, 0});
    vector<int> argBest(sz, -1);
    vector<int> parent(sz, -1);
    vector<int> order;
    order.reserve(sz);

    // Find any node that actually appears in the edges to use as root
    int root = edges.empty() ? 0 : edges[0].first;

    vector<int> stack = {root};
    vector<bool> visited(sz, false);
    visited[root] = true;
    while (!stack.empty()) {
        int u = stack.back(); stack.pop_back();
        order.push_back(u);
        for (int v : adj[u]) {
            if (visited[v]) continue;
            visited[v] = true;
            parent[v] = u;
            stack.push_back(v);
        }
    }

    // dfs1: post-order
    for (int i = (int)order.size() - 1; i >= 0; i--) {
        int node = order[i];
        for (int adjN : adj[node]) {
            if (adjN == parent[node]) continue;
            int cand = down2[adjN][0] + 1;
            if (cand >= down2[node][0]) {
                down2[node][1] = down2[node][0];
                down2[node][0] = cand;
                argBest[node] = adjN;
            } else if (cand > down2[node][1]) {
                down2[node][1] = cand;
            }
        }
    }

    // dfs2: pre-order
    vector<int> up(sz, 0), res(sz, 0);
    for (int node : order) {
        res[node] = max(up[node], down2[node][0]);
        for (int child : adj[node]) {
            if (child == parent[node]) continue;
            int bestDownExcl = (argBest[node] == child) ? down2[node][1] : down2[node][0];
            up[child] = max(up[node] + 1, bestDownExcl + 1);
        }
    }

    return res;
}