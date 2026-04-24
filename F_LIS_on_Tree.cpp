#include<bits/stdc++.h>
using namespace std;

struct RollbackLis {
    vector<int> dp = {INT_MIN}; // dp[i] is the smallest ending number for a sequence of length i
    vector<pair<int,int>> history; // (-1, 0) means a pushback, otherwise (i, oldV) indicates what we should have

    void add (int v) {
        // since we are strictly increasing for this problem, binary search for the smallest value we are <=, if none, append, or another view is rightmost we are greater than, and add to the next occurrence on the right
        int l = 0;
        int r = dp.size() - 1;
        int resI = -1;
        while (l <= r) {
            int m = (r + l) / 2;
            if (v <= dp[m]) {
                resI = m;
                r = m - 1;
            } else {
                l = m + 1;
            }
        }
        if (resI == -1) {
            dp.push_back(v);
            history.push_back({-1, 0});
        } else {
            history.push_back({resI, dp[resI]});
            dp[resI] = v;
        }
    }

    void undo() {
        if (!history.size()) return;
        pair<int,int> hist = history.back(); history.pop_back();
        if (hist.first == -1) {
            dp.pop_back();
            return;
        }
        dp[hist.first] = hist.second;
    }

    int lis() {
        return dp.size() - 1;
    }
};

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n; cin >> n;
    vector<int> arr(n + 1);
    for (int i = 0; i < n; i++) {
        cin >> arr[i + 1];
    }
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<vector<int>> children(n + 1);
    auto make = [&](auto&& self, int node, int parent) -> void {
        for (auto adjN : adj[node]) {
            if (adjN == parent) continue;
            children[node].push_back(adjN);
            self(self, adjN, node);
        }
    };
    make(make, 1, 0);

    vector<int> res(n + 1);

    RollbackLis lis;

    auto dfs = [&](auto&& self, int node) -> void {
        lis.add(arr[node]);
        res[node] = lis.lis();
        for (auto child : children[node]) {
            self(self, child);
        }
        lis.undo();
    };

    dfs(dfs, 1);

    for (int i = 1; i < n + 1; i++) cout << res[i] << endl;
}