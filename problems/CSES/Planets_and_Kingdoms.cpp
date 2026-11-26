#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<int>> g(n + 1);
    vector<vector<int>> revG(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        g[a].push_back(b);
        revG[b].push_back(a);
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
    
    vector<int> componentId(n + 1, -1);
    int nextComponent = 1;

    auto revDfs = [&](auto&& self, int node) -> void {
        componentId[node] = nextComponent;
        for (auto adjN : revG[node]) {
            if (componentId[adjN] != -1) continue;
            self(self, adjN);
        }
    };

    for (int i = finishOrder.size() - 1; i >= 0; i--) {
        int node = finishOrder[i];
        if (componentId[node] == -1) {
            revDfs(revDfs, node);
            nextComponent++;
        }
    }

    cout << nextComponent - 1 << endl;
    for (int i = 1; i < componentId.size(); i++) {
        cout << componentId[i] << " ";
    }
}