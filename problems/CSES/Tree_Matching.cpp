#include <bits/stdc++.h>
using namespace std;

int main() {
    int n; cin >> n;
    vector<vector<int>> g(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        g[a].push_back(b);
        g[b].push_back(a);
    }

    // returns # of edges placed, if that child is part of an edge
    auto dfs = [&](auto&& self, int node, int parent) -> pair<int,bool> { 
        if (g[node].size() == 1 && node != 0) {
            return {0, false};
        }
        int edges = 0;
        bool notTouchingChild = false;
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            auto p = self(self, adj, node);
            if (!p.second) {
                notTouchingChild = true;
            }
            edges += p.first;
        }
        if (notTouchingChild) {
            edges++;
            return {edges, true};
        } else {
            return {edges, false};
        }
    };
    auto ans = dfs(dfs, 0, -1);
    cout << ans.first;
}