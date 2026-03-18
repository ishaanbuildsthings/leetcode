#include <bits/stdc++.h>
using namespace std;

void solve() {
    // cout << "----------" << endl;
    int n; cin >> n;
    vector<int> vals(n + 1); for (int i = 0; i < n; i++) cin >> vals[i + 1];
    vector<int> parents(n - 1); for (int i = 0; i < n - 1; i++) cin >> parents[i];
    vector<vector<int>> children(n + 1);
    for (int node = 2; node <= n; node++) {
        children[parents[node - 2]].push_back(node);
    }
    // for (int node = 1; node <= n; node++) {
    //     cout << "children of node: " << node << ":" << endl;
    //     for (auto x : children[node]) {
    //         cout << x << " ";
    //     }
    //     cout << endl;
    // }

    // 1
    //2 3
    //   4

    // vals
    // 0
    //1 0
    //   2

    auto dfs = [&](auto&& self, int node) -> long long {
        if (children[node].size() == 0) {
            return vals[node];
        }
        long long bottle = vals[node];

        vector<long long> childBottles;
        long long minCb = LLONG_MAX / 4;
        for (auto child : children[node]) {
            long long cb = self(self, child);
            childBottles.push_back(cb);
            minCb = min(minCb, cb);
        }
        if (minCb < bottle) {
            if (node == 1) {
                return minCb + vals[node];
            }
            return minCb;
        }
        // we sap from the min child bottleneck
        long long diff = minCb - bottle;
        long long saps = diff / 2;
        if (node == 1) {
            return minCb + vals[node];
        }
        return bottle + saps;
    };

    long long ans = dfs(dfs, 1);

    cout << ans << '\n';

    // every dfs will send up a bottleneck
    // either the bottleneck below us
    // or we find the smallest in our subtree and sap from it
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}