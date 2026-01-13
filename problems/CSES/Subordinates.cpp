#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<vector<int>> g(n);
    for (int i = 0; i < n - 1; i++) {
        int parent; cin >> parent; parent--;
        g[i + 1].push_back(parent);
        g[parent].push_back(i + 1);
    }


    vector<int> sz(n, 1);

    auto dfs = [&](auto&& self, int node, int parent) -> void {
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            self(self, adj, node);
            sz[node] += sz[adj];
        }
    };
    dfs(dfs, 0, -1);

    for (int node = 0; node < n; node++) {
        cout << sz[node] - 1 << " ";
    }
}