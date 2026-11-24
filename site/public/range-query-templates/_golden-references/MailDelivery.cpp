// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/golden-references/MailDelivery.cpp
// Euler circuit (Hierholzer) on an undirected graph, as a full solution to CSES "Mail Delivery"
// (https://cses.fi/problemset/task/1691).
// A circuit exists when every node has even degree and every edge is reachable. The reachability part is checked
// after the dfs instead of with a separate component search: if the path doesn't hold every edge (m + 1 nodes), some
// edges were in a piece the start never reaches.
// Undirected twist: each edge sits in both endpoints' lists, so edges carry an id and a used flag, and the dfs skips
// the copy that was already walked from the other side.
// O(n + m) time and space.
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<pair<int,int>>> g(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back({b, i});
        g[b].push_back({a, i});
    }
    for (int node = 1; node <= n; node++) {
        if (g[node].size() % 2) {
            cout << "IMPOSSIBLE" << endl;
            return 0;
        }
    }

    deque<int> path;
    vector<bool> usedEdges(m + 1, false);

    auto dfs = [&](auto&& self, int node) -> void {
        while (g[node].size()) {
            auto [nxt, id] = g[node].back(); g[node].pop_back();
            if (usedEdges[id]) continue;
            usedEdges[id] = true;
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