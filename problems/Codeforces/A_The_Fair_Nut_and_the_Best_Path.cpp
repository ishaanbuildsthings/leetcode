#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<ll> gas(n + 1); for (int i = 0; i < n; i++) cin >> gas[i + 1];
    vector<vector<pair<int,ll>>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        ll w; cin >> w;
        adj[a].push_back({b, w});
        adj[b].push_back({a, w});
    }
    vector<vector<pair<int,ll>>> children(n + 1);
    auto make = [&](auto&& self, int node, int parent) -> void {
        for (auto [adjN, adjW] : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back({adjN, adjW});
            self(self, adjN, node);
        }
    };
    make(make, 1, 0);

    ll res = 0;

    // most gas we can get up to this node
    auto dfs = [&](auto&& self, int node) -> ll {
        if (!children[node].size()) {
            res = max(res, gas[node]);
            return gas[node];
        }
        vector<ll> options;
        for (auto [child, w] : children[node]) {
            ll childVal = self(self, child);
            if (childVal - w < 0) continue;
            ll nval = childVal - w;
            options.push_back(nval);
        }
        options.push_back(0);
        options.push_back(0); // simulate two dummy paths
        sort(options.begin(), options.end());
        ll mx1 = options[options.size()-1];
        ll mx2 = options[options.size()-2];
        ll path = mx1 + mx2 + gas[node];
        res = max(res, path);
        return mx1 + gas[node];
    };
    dfs(dfs, 1);

    cout << res;
}