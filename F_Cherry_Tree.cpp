#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int t; cin >> t;
    while (t--) {
        int n; cin >> n;
        vector<vector<int>> adj(n + 1);
        vector<vector<int>> children(n + 1);
        for (int i = 0; i < n - 1; i++) {
            int a, b; cin >> a >> b;
            adj[a].push_back(b);
            adj[b].push_back(a);
        }
        auto fillDfs = [&](auto&& self, int node, int parent) -> void {
            for (auto adjN : adj[node]) {
                if (adjN == parent) continue;
                children[node].push_back(adjN);
                self(self, adjN, node);
            }
        };
        fillDfs(fillDfs, 1, 0);

        auto merge = [&](vector<int>& left, vector<int>& right) -> vector<int> {
            vector<int> merged = {0, 0, 0};
            for (int shakeLeft = 0; shakeLeft <= 2; shakeLeft++) {
                for (int shakeRight = 0; shakeRight <= 2; shakeRight++) {
                    int rem = (shakeLeft + shakeRight) % 3;
                    if (left[shakeLeft] && right[shakeRight]) {
                        merged[rem] = 1;
                    }
                }
            }
            return merged;
        };

        vector<vector<int>> dp(n + 1); // dp[node][remainderShakes] means that is doable

        auto dfs = [&](auto&& self, int node) -> void {
            // leaf
            if (children[node].size() == 0) {
                dp[node] = {0, 1, 0};
                return;
            }

            // process children first
            for (auto child : children[node]) {
                self(self, child);
            }

            int firstChild = children[node][0];
            vector<int>& oldDp = dp[firstChild];
            for (int i = 1; i < children[node].size(); i++) {
                int child = children[node][i];
                vector<int>& childDp = dp[child];
                auto merged = merge(oldDp, childDp);
                oldDp = move(merged);
            }

            oldDp[1] = 1; // shake the entire tree
            dp[node] = move(oldDp);
        };

        dfs(dfs, 1);

        cout << (dp[1][0] == 1 ? "YES" : "NO") << endl;
    }
}