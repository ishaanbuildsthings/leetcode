#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n;
  cin >> n;
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  int q;
  cin >> q;

  int LOG = 32 - __builtin_clz(n);

  vector<vector<int>> up(LOG, vector<int>(n + 1));
  vector<int> depths(n + 1);

  function<void(int, int)> dfs = [&](int node, int parent) {
    up[0][node] = parent;
    depths[node] = node == 1 ? 0 : depths[parent] + 1;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
    for (auto child : adj[node]) {
      if (child != parent) {
        dfs(child, node);
      }
    }
  };
  dfs(1, 1);

  function<int(int,int)> kthAncestor = [&](int node, int kth) {
    for (int k = 0; k < LOG; k++) if (kth >> k & 1) node = up[k][node];
    return node;
  };

  function <int(int,int)> lca = [&](int a, int b) {
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

  function <int(int,int,int)> aToBX = [&](int a, int b, int x) {
    int ab = lca(a, b);
    int distaAB = depths[a] - depths[ab];
    if (x <= distaAB) return kthAncestor(a, x);
    int distbAB = depths[b] - depths[ab];
    int remain = x - distaAB;
    if (remain >= distbAB) return b;
    return kthAncestor(b, distbAB - remain);
  };

  for (int i = 0; i < q; i++) {
    int a, b, c;
    cin >> a >> b >> c;
    cout << aToBX(a, b, c) << endl;
  }
}