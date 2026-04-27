#include <bits/stdc++.h>
using namespace std;

void solve() {
    int n; cin >> n;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<vector<int>> children(n + 1);
    auto make = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    make(make, 1, 0);

    vector<int> size(n + 1);
    auto dfs = [&](auto&& self, int node) -> void {
        if (children[node].size() == 0) {
            size[node] = 1;
            return;
        }
        int sizeHere = 1;
        for (auto child : children[node]) {
            self(self, child);
            sizeHere += size[child];
        }
        size[node] = sizeHere;
    };
    dfs(dfs, 1);

    auto recurse = [&](auto&& self, int node) -> int {
        if (children[node].size() == 0) return 0;
        if (children[node].size() == 1) {
            return size[children[node][0]] - 1;
        }
        int cutFirst = size[children[node][0]] - 1 + self(self, children[node][1]);
        int cutSecond = size[children[node][1]] - 1 + self(self, children[node][0]);
        return max(cutFirst, cutSecond);
    };

    auto ans = recurse(recurse, 1);
    cout << ans << endl;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}