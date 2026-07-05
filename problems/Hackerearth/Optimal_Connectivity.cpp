#include <bits/stdc++.h>
using namespace std;
 
struct DSU {
  vector<int> p;
  vector<int> sz;
  DSU(int n) {
    sz.assign(n + 1, 1);
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0);
  }
  int find(int a) { return p[a] == a ? a : p[a] = find(p[a]); }
  bool unite(int a, int b) {
    int l1 = find(a), l2 = find(b);
    if (l1 == l2) return false;
    int s1 = sz[l1], s2 = sz[l2];
    if (s1 > s2) swap(l1, l2);
    sz[l2] += sz[l1];
    p[l1] = l2;
    return true;
  }
  bool same(int a, int b) { return find(a) == find(b); }
};
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
 
  int n;
  cin >> n;
 
  vector<vector<pair<int,int>>> edges(n + 1); // edges[node] -> {adjNode, weight}
  for (int i = 0; i < n - 1; i++) {
    int a, b, w;
    cin >> a >> b >> w;
    edges[a].push_back({b, w});
    edges[b].push_back({a, w});
  }
 
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
  vector<vector<int>> mx(LOG, vector<int>(n + 1));
  vector<int> depths(n + 1);
 
  function<void(int,int,int)> dfs = [&](int node, int parent, int wToP) {
    up[0][node] = parent;
    mx[0][node] = wToP;
    depths[node] = (node == 1 ? 0 : depths[parent] + 1);
 
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
      mx[k][node] = max(mx[k-1][node], mx[k-1][mid]);
    }
 
    for (auto [adj, w] : edges[node]) {
      if (adj == parent) continue;
      dfs(adj, node, w);
    }
  };
  dfs(1, 1, 0); // root at 1
 
  function<int(int,int)> mxOnPath = [&](int a, int b) {
    int res = 0;
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if ((diff >> k) & 1) {
        res = max(res, mx[k][a]);
        a = up[k][a];
      }
    }
    if (a == b) return res;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        res = max(res, max(mx[k][a], mx[k][b]));
        a = up[k][a];
        b = up[k][b];
      }
    }
    res = max(res, max(mx[0][a], mx[0][b]));
    return res;
  };
 
  int q;
  cin >> q;
  while (q--) {
    int u, v, w;
    cin >> u >> v >> w;
    cout << (w < mxOnPath(u, v) ? "YES" : "NO") << '\n';
  }
}