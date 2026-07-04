#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  vector<vector<int>> adj(n);
  for (int i = 0; i < n - 1; i++) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n));
  vector<int> depths(n);
  function<void(int,int)> dfs = [&](int node, int parent) {
    up[0][node] = parent;
    depths[node] = node == 0 ? 0 : depths[parent] + 1;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
    for (auto adjN : adj[node]) {
      if (adjN != parent) dfs(adjN, node);
    }
  };

  function<int(int,int)> kth = [&](int node, int kth) {
    for (int k = 0; k < LOG; k++) if (kth >> k & 1) node = up[k][node];
    return node;
  };

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

  dfs(0, 0);
  for (int i = 0; i < q; i++) {
    int a, b, x;
    cin >> a >> b >> x;
    int ab = lca(a, b);
    int aToAB = depths[a] - depths[ab];
    if (aToAB >= x) {
      cout << kth(a, x) << endl;
      continue;
    }
    int remain = x - aToAB;
    int bToAB = depths[b] - depths[ab];
    if (remain > bToAB) {
      cout << -1 << endl;
    } else {
      cout << kth(b, bToAB - remain) << endl;
    }
  }
}