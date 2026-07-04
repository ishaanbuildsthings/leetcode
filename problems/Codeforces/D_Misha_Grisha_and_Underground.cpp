#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  vector<vector<int>> adj(n + 1); // adj[node] is a list of nodes
  for (int i = 0; i < n - 1; i++) {
    int v;
    cin >> v;
    adj[i+2].push_back(v);
    adj[v].push_back(i + 2);
  }
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n+1)); // up[k][u]
  vector<int> depths(n + 1);
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
    // make a deeper
    if (depths[a] < depths[b]) swap(a, b);
    // bring a to b level
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) a = up[k][a];
    }
    if (a == b) return a;
    // bring a and b up while their LCAs do not touch
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        a = up[k][a];
        b = up[k][b];
      }
    }
    return up[0][a];
  };

  // # of nodes on path
  function<int(int,int)> dist = [&](int a, int b) {
    int ab = lca(a, b);
    int aToAB = depths[a] - depths[ab] + 1;
    int bToAB = depths[b] - depths[ab] + 1;
    return aToAB + bToAB - 1;
  };

  for (int i = 0; i < q; i++) {
    int a, b, c;
    cin >> a >> b >> c;
    array<int,3> arr = {a, b, c};
    sort(arr.begin(), arr.end(), [&](int u, int v) {
      return depths[u] > depths[v];
    });
    int m = lca(a,b) ^ lca(a,c) ^ lca(b,c);
    cout << max(dist(m, a), max(dist(m, b), dist(m, c))) << endl;
  }
}