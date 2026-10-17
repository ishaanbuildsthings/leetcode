#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
    }

    vector<bool> inPath(n + 1, false);
    vector<bool> seen(n + 1, false);

    bool ansFound = false;

    auto dfs = [&](auto&& self, int node, vector<int>& path) -> void {
        inPath[node] = true;
        seen[node] = true;
        path.push_back(node);
        for (auto adjN : adj[node]) {
            if (ansFound) return;
            if (inPath[adjN]) {
                ansFound = true;
                int idx = find(path.begin(), path.end(), adjN) - path.begin();
                int sz = path.size() - idx + 1;
                cout << sz << '\n';
                for (int i = idx; i < path.size(); i++) {
                    cout << path[i] << ' ';
                }
                cout << adjN << ' ';
                return;
            }
            if (seen[adjN]) {
                continue;
            }
            if (ansFound) return;
            self(self, adjN, path);
        }
        inPath[node] = false;
        path.pop_back();
    };
    for (int node = 1; node <= n; node++) {
        if (!seen[node] && !ansFound) {
            vector<int> path;
            dfs(dfs, node, path);
        }
    }

    if (!ansFound) {
        cout << "IMPOSSIBLE" << '\n';
    }
}