#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int t;
  cin >> t;
  int init = t;
  while (t--) {
    cout << "Case " << init - t << ":" << endl;
    int n;
    cin >> n;
    int LOG = 32 - __builtin_clz(n);
    vector<vector<pair<int,int>>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
      int u, v, w;
      cin >> u >> v >> w;
      adj[u].push_back({v, w});
      adj[v].push_back({u, w});
    }
    vector<vector<int>> up(LOG, vector<int>(n + 1));
    vector<vector<int>> gcdUp(LOG, vector<int>(n + 1));
    function<void(int,int,int)> dfs = [&](int node, int parent, int wToP) {
      up[0][node] = parent;
      gcdUp[0][node] = wToP;
      for (int k = 1; k < LOG; k++) {
        int mid = up[k-1][node];
        up[k][node] = up[k-1][mid];
        gcdUp[k][node] = gcd(gcdUp[k-1][node], gcdUp[k-1][mid]);
      }
      for (auto [adjNode, adjW] : adj[node]) {
        if (adjNode == parent) continue;
        dfs(adjNode, node, adjW);
      }
    };
    dfs(1, 1, 0);
    int q;
    cin >> q;
    for (int i = 0; i < q; i++) {
      int start, p;
      cin >> start >> p;
      for (int k = LOG - 1; k >= 0; k--) {
        int gUp = gcdUp[k][start];
        if (gUp % p == 0) start = up[k][start];
      }
      cout << start << endl;
    }
  }
}