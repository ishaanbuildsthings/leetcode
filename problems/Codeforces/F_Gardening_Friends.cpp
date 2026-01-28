#include <bits/stdc++.h>
using namespace std;

void solve() {
    int n, k, c; cin >> n >> k >> c;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<pair<int,int>> down2(n + 1); // down2.first = max dist, down2.second = max dist through a second child
    vector<int> depths(n + 1);
    auto dfs1 = [&](auto&& self, int node, int parent, int depth) -> void {
        depths[node] = depth;
        // leaf
        if (node != 1 && adj[node].size() == 1) {
            down2[node] = {0, 0};
            return;
        }
        int mx1 = 0;
        int mx2 = 0;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            self(self, adjN, node, depth + 1);
        }
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            int nd = 1 + down2[adjN].first;
            if (nd > mx1) {
                mx2 = mx1;
                mx1 = nd;
            } else if (nd == mx1) {
                mx2 = nd;
            } else if (nd > mx2) {
                mx2 = nd;
            }
        }
        down2[node] = {mx1, mx2};
    };
    dfs1(dfs1, 1, 0, 0);

    vector<int> up(n + 1);
    auto dfs2 = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            int bestThroughParent;
            if (down2[node].first == 1 + down2[adjN].first) {
                bestThroughParent = 1 + down2[node].second;
            } else {
                bestThroughParent = 1 + down2[node].first;
            }
            bestThroughParent = max(bestThroughParent, 1 + up[node]);
            up[adjN] = bestThroughParent;
            self(self, adjN, node);
        }
    };
    dfs2(dfs2, 1, 0);
    long long out = 0;
    for (int node = 1; node <= n; node++) {
        long long profit = 1LL * max(down2[node].first, up[node]) * k;
        long long cost = 1LL * c * depths[node];
        out = max(out, profit - cost);
    }
    cout << out << '\n';
}

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}

// 5
// 1 6 2 3
// 4