#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<int>> g(n + 1);
    vector<int> inDeg(n + 1, 0);
    vector<int> outDeg(n + 1, 0);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
        inDeg[b]++;
        outDeg[a]++;
    }

    bool fail = false;
    if (outDeg[1] != inDeg[1] + 1) fail = true;
    if (inDeg[n] != outDeg[n] + 1) fail = true;
    for (int node = 2; node < n; node++) {
        if (inDeg[node] != outDeg[node]) fail = true;
    }

    if (fail) {
        cout << "IMPOSSIBLE" << endl;
        return 0;
    }

    deque<int> path;

    auto dfs = [&](auto&& self, int node) -> void {
        while (g[node].size()) {
            int nxt = g[node].back(); g[node].pop_back();
            self(self, nxt);
        }
        path.push_front(node);
    };
    dfs(dfs, 1);

    if (path.size() != m + 1) {
        cout << "IMPOSSIBLE" << endl;
        return 0;
    }

    for (auto x : path) cout << x << " ";
    cout << endl;
}