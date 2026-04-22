#include<bits/stdc++.h>
using namespace std;

// Returns vector where res[i] = sum of distances from node i to all other nodes.
// numNodes is the number of nodes in the tree.
// Node labels must be either 0-indexed in [0, numNodes) or 1-indexed in [1, numNodes].
// res has size numNodes + 1; the unused slot (res[0] or res[numNodes]) is 0.
// Uses long long because sums of distances can reach ~n^2/2 on a path graph.
vector<long long> treeSumOfDistances(int numNodes, const vector<pair<int,int>>& edges) {
    int sz = numNodes + 1;
    vector<vector<int>> adj(sz);
    for (auto [a, b] : edges) {
        adj[a].push_back(b);
        adj[b].push_back(a);
    }

    vector<int> parent(sz, -1);
    vector<int> order;
    order.reserve(sz);

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

    // dfs1: post-order — subtree sizes and down[u] = sum of dist from u into its subtree
    vector<int> sub(sz, 1);
    vector<long long> down(sz, 0);
    for (int i = (int)order.size() - 1; i >= 0; i--) {
        int node = order[i];
        for (int child : adj[node]) {
            if (child == parent[node]) continue;
            sub[node] += sub[child];
            down[node] += down[child] + sub[child];
        }
    }

    // dfs2: pre-order — reroot. For child c of u: full[c] = full[u] - sub[c] + (n - sub[c])
    vector<long long> full(sz, 0);
    full[root] = down[root];
    for (int node : order) {
        for (int child : adj[node]) {
            if (child == parent[node]) continue;
            full[child] = full[node] - sub[child] + (long long)(numNodes - sub[child]);
        }
    }

    return full;
}