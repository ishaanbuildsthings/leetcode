#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m;
  cin >> n >> m;
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }

  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
  vector<int> depths(n + 1);

  function<void(int,int)> dfs = [&](int node, int parent) {
    up[0][node] = parent;
    depths[node] = node == 1 ? 0 : depths[parent] + 1;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
    for (auto child : adj[node]) {
      if (child == parent) continue;
      dfs(child, node);
    }
  };
  dfs(1, 1);

  function<int(int,int)> lca = [&](int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) if (diff >> k & 1) a = up[k][a];
    if (a == b) return a;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        a = up[k][a];
        b = up[k][b];
      }
    }
    return up[0][a];
  };

  function<int(int,int,int)> geodesic = [&](int a, int b, int c) {
    return lca(a, b) ^ lca(a, c) ^ lca(b, c);
  };

  function<int(int,int)> dist = [&](int a, int b) {
    int ab = lca(a, b);
    return depths[a] + depths[b] - 2 * depths[ab];
  };

  for (int i = 0; i < m; i++) {
    int verts;
    cin >> verts;
    vector<int> nodes;
    for (int j = 0; j < verts; j++) {
      int x;
      cin >> x;
      nodes.push_back(x);
    }
    int deepest = 0;
    int deepestNode = 1;
    for (auto vert : nodes) {
      if (depths[vert] > deepest) {
        deepest = depths[vert];
        deepestNode = vert;
      }
    }
    int fail = 0;
    for (auto vert : nodes) {
      int geo = geodesic(1, deepestNode, vert);
      if (dist(vert, geo) > 1) {
        fail = 1;
        break;
      }
    }
    cout << ((fail == 0) ? "YES" : "NO") << endl;
  }
}