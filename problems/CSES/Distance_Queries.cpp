#include <bits/stdc++.h>
using namespace std;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  vector<int> depths(n + 1);
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
 
  function<void(int,int)> dfs = [&](int node, int parent) {
    up[0][node] = parent;
    depths[node] = node == 1 ? 0 : depths[parent] + 1;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
    for (auto adjNode : adj[node]) {
      if (adjNode == parent) continue;
      dfs(adjNode, node);
    }
  };
  dfs(1, 1);
 
  function<int(int,int)> lca = [&](int a, int b) {
    if (depths[a] < depths[b]) swap(a, b); // make a deeper
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) a = up[k][a];
    }
    if (a == b) return a;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        a = up[k][a];
        b = up[k][b];
      }
    }
    return up[0][a];
  };
 
  function<int(int,int)> dist = [&](int a, int b) {
    int ab = lca(a, b);
    return depths[a] + depths[b] - 2 * depths[ab];
  };
 
  for (int i = 0; i < q; i++) {
    int a, b;
    cin >> a >> b;
    cout << dist(a, b) << endl;
  }
 
}