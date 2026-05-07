#include <bits/stdc++.h>
using namespace std;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  vector<int> es;
  es.resize(n + 1);
  vector<vector<int>> children(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int boss;
    cin >> boss;
    es[i+2] = boss;
    children[boss].push_back(i + 2);
  }
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1)); // up[k][v] = the ancestor
  vector<int> depths(n + 1);
  // fill out the up table
  function<void(int,int)> dfs = [&](int node, int parent) {
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
  dfs(1, 1); // parent is itself
  for (int i = 0; i < q; i++) {
    int a, levels;
    cin >> a >> levels;
    if (depths[a] < levels) {
      cout << -1 << endl;
      continue;
    }
    for (int k = 0; k < LOG; k++) {
      if (levels >> k & 1) {
        a = up[k][a];
      }
    }
    cout << a << endl;
  }
}