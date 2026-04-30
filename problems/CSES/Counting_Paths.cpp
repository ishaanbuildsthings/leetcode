#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<pair<int,int>> edges;
    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
        int a, b; cin >> a >> b; a--; b--;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    vector<int> parents(n, -1);
    vector<vector<int>> children(n);
    vector<int> depths(n, 0);
    auto init = [&](auto&& self, int node, int parent, int currDepth) -> void {
      if (parent != -1) {
        parents[node] = parent;
      }  
      depths[node] = currDepth;
      for (auto adjN : adj[node]) {
        if (adjN == parent) continue;
        children[node].push_back(adjN);
        self(self, adjN, node, currDepth + 1);
      }
    };
    init(init, 0, -1, 0);

    int LOG = 20;
    vector<vector<int>> lift(LOG, vector<int>(n)); // lift[power][node] = that ancestor
    for (int node = 0; node < n; node++) {
        lift[0][node] = parents[node];
    }
    for (int power = 1; power < LOG; power++) {
        for (int node = 0; node < n; node++) {
            int half = lift[power - 1][node];
            if (half == -1) {
                lift[power][node] = -1;
            } else {
                int full = lift[power - 1][half];
                lift[power][node] = full;
            }
        }
    }

    auto kthAncestor = [&](int node, int k) -> int {
        int curr = node;
        for (int b = 0; b < LOG; b++) {
            if ((1 << b) & k) {
                curr = lift[b][curr];
                if (curr == -1) return -1;
            }
        }
        return curr;
    };

    auto lca = [&](int a, int b) -> int {
        if (depths[a] < depths[b]) swap(a, b);
        int diff = depths[a] - depths[b];
        a = kthAncestor(a, diff);
        if (a == b) return a;
        for (int bit = LOG - 1; bit >= 0; bit--) {
            int up1 = lift[bit][a];
            int up2 = lift[bit][b];
            if (up1 != up2) {
                a = up1;
                b = up2;
            }
        }
        return parents[a];
    };

    vector<int> diffs(n, 0); // contribution flowing up from node

    vector<pair<int,int>> paths;
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b; a--; b--;
        diffs[a]++;
        diffs[b]++;
        int lcaVal = lca(a, b);
        diffs[lcaVal]--;
        if (parents[lcaVal] != -1) {
            diffs[parents[lcaVal]]--;
        }
    }

    vector<int> res(n);
    auto dfs = [&](auto&& self, int node) -> int {
        int currPaths = diffs[node];
        for (auto child : children[node]) {
            currPaths += self(self, child);
        }
        res[node] = currPaths;
        return currPaths;
    };
    dfs(dfs, 0);

    for (auto x : res) cout << x << " ";
}