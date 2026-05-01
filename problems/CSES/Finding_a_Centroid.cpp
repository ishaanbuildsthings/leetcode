#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<int> sz(n);
    int res = -1;
    auto dfs = [&](auto&& self, int node, int parent) -> void {
        int belowMax = 0;
        int szHere = 1;
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            self(self, adjN, node);
            belowMax = max(belowMax, sz[adjN]);
            szHere += sz[adjN];
        }
        sz[node] = szHere;
        int szUp = n - szHere;
        if (szUp <= n / 2 && belowMax <= n / 2) res = node;
    };
    dfs(dfs, 0, -1);
    cout << res + 1 << '\n';
}