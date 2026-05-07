#include <bits/stdc++.h>
using namespace std;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  vector<vector<int>> children(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int boss;
    cin >> boss;
    children[boss].push_back(i+2);
  }
  vector<int> depths(n + 1);
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
  function<void(int, int)> dfs = [&](int node, int parent) {
    up[0][node] = parent;
    depths[node] = node == 1 ? 0 : depths[parent] + 1;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
    for (auto child : children[node]) {
      dfs(child, node);
    }
  };
  dfs(1, 1);
  for (int i = 0; i < q; i++) {
    int a, b;
    cin >> a >> b;
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) a = up[k][a];
    }
    if (a == b) {
      cout << a << endl;
      continue;
    }
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        a = up[k][a];
        b = up[k][b];
      }
    }
    cout << up[0][a] << endl;
  }
}