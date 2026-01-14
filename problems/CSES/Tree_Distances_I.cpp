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

    vector<int> best1(n); // best distance below
    vector<int> best2(n); // second best distance below (must use different child)

    auto dfs = [&](auto&& self, int node, int parent) -> void {
        int b1 = 0;
        int b2 = -1;
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            self(self, adj, node);
            auto distWithChild = best1[adj] + 1;
            if (distWithChild > b1) {
                b2 = b1;
                b1 = distWithChild;
            } else if (distWithChild > b2) {
                b2 = distWithChild;
            }
        }
        best1[node] = b1;
        best2[node] = b2;
    };
    dfs(dfs, 0, -1);

    vector<int> out(n);
    out[0] = best1[0];
    vector<int> up(n); // up[0] automatically 0, nowhere to go up

    auto dfs2 = [&](auto&& self, int node, int parent) -> void {
        for (auto adj : g[node]) {
            if (adj == parent) continue;
            // solving for adj
            
            // option 1, we go down from adj
            int option1 = best1[adj];

            // option 2, we take an up from the parent + 1
            int option2 = up[node] + 1;

            // option 3, we go down from the parent, but not through us
            int option3;
            if (best1[node] == best1[adj] + 1) {
                option3 = 1 + best2[node];
            } else {
                option3 = 1 + best1[node];
            }

            out[adj] = max({option1, option2, option3});
            up[adj] =  max(up[node] + 1, option3);

            self(self, adj, node);
        }
    };
    dfs2(dfs2, 0, -1);

    for (auto x : out) cout << x << " ";

}