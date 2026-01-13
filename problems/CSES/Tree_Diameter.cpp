#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<vector<int>> g(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        g[a].push_back(b);
        g[b].push_back(a);
    }
    int result = 1;
    auto dfs = [&](auto&& self, int parent, int node) -> int {
        int chain = 1;
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            int adjChain = self(self, node, adj);
            result = max(result, chain + adjChain);
            chain = max(chain, adjChain + 1);
        }
        return chain;
    };
    dfs(dfs, -1, 0);

    cout << result - 1;
}