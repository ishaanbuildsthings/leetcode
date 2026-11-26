#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;

    vector<vector<int>> g(n + 1);
    vector<vector<int>> rev(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
        rev[b].push_back(a);
    }

    vector<int> finishOrder;
    vector<bool> seen(n + 1, false);

    auto forwardDfs = [&](auto&& self, int node) -> void {
        seen[node] = true;
        for (auto adjN : g[node]) {
            if (seen[adjN]) continue;
            self(self, adjN);
        }
        finishOrder.push_back(node);
    };
    for (int node = 1; node <= n; node++) {
        if (!seen[node]) forwardDfs(forwardDfs, node);
    }

    // not in graph anymore
    vector<bool> used(n + 1, false);

    auto revDfs = [&](auto&& self, int node) -> void {
        used[node] = true;
        for (auto adjN : rev[node]) {
            if (used[adjN]) continue;
            self(self, adjN);
        }
    };

    vector<int> roots;
    for (int i = finishOrder.size() - 1; i >= 0; i--) {
        int node = finishOrder[i];
        if (used[node]) continue;
        roots.push_back(node);
        revDfs(revDfs, node);
    }

    if (roots.size() == 1) {
        cout << "YES";
    } else {
        cout << "NO";
        cout << endl << roots[1] << " " << roots[0];
    }
}