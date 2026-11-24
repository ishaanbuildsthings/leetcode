// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/TeleportersPath.cpp
// Euler path (Hierholzer) on a directed graph, as a full solution to CSES "Teleporters Path"
// (https://cses.fi/problemset/task/1693).
// A path from start to end exists when the start has one more out than in, the end has one more in than out, every
// other node has in equal to out, and every edge is reachable. The reachability part is checked after the dfs: if the
// path doesn't hold every edge (m + 1 nodes), some edges were in a piece the start never reaches.
// O(n + m) time and space.
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