#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m, q; cin >> n >> m >> q;

  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1)); // up[k][u] is the ancestor
  vector<vector<vector<int>>> upBest(LOG, vector<vector<int>>(n + 1)); // upBest[k][u] is the a smallest [idx, idx, ...]
  vector<int> depths(n + 1);
  vector<vector<int>> adj(n + 1); // adj[node] -> [adjNode, adjNode]
  for (int i = 0; i < n - 1; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }

  vector<vector<int>> cityToIds(n + 1); // city -> [idx, idx, idx, ...]

  for (int idx = 0; idx < m; idx++) {
    int city; cin >> city;
    cityToIds[city].push_back(idx + 1);
  }
  for (auto &bucket : cityToIds) {
    sort(bucket.begin(), bucket.end());
    while (bucket.size() > 10) bucket.pop_back();
  }

  auto merge = [&](const vector<int>& a, const vector<int>& b) -> vector<int> {
    vector<int> r; r.reserve(20);
    int i = 0, j = 0;
    while ((int)r.size() < 10 && (i < (int)a.size() || j < (int)b.size())) {
      int va = i < (int)a.size() ? a[i] : INT_MAX;
      int vb = j < (int)b.size() ? b[j] : INT_MAX;
      if (va < vb) { r.push_back(va); i++; } else { r.push_back(vb); j++; }
    }
    return r;
  };

  function<void(int,int)> dfs = [&](int node, int parent) {
    depths[node] = node == 1 ? 0 : depths[parent] + 1;
    up[0][node] = parent;
    upBest[0][node] = cityToIds[node];
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
      auto bottomBest = upBest[k-1][node];
      auto topBest = upBest[k-1][mid];
      vector<int> resBest = merge(bottomBest, topBest);
      upBest[k][node] = resBest;
    }
    for (auto child : adj[node]) {
      if (child != parent) dfs(child, node);
    }
  };
  dfs(1, 1);

  function<vector<int>(int,int)> pathBest = [&](int a, int b) {
    vector<int> res; // our 10 best from a<>b
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        auto chainBest = upBest[k][a];
        res = merge(res, chainBest);
        a = up[k][a];
      }
    }
    if (a == b) {
      res = merge(res, cityToIds[a]);
      return res;
    };
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        auto aBest = upBest[k][a];
        res = merge(res, aBest);
        res = merge(res, upBest[k][b]);
        a = up[k][a];
        b = up[k][b];
      }
    }
    res = merge(res, upBest[0][a]);
    res = merge(res, upBest[0][b]);
    res = merge(res, cityToIds[up[0][a]]); // add the LCA values 1 time
    return res;
  };

  while (q--) {
    int a, b, amount; cin >> a >> b >> amount;
    auto ids = pathBest(a, b);
    cout << min((int)ids.size(), amount) << " ";
    for (int j = 0; j < min(amount, (int)ids.size()); j++)
    cout << ids[j] << " ";
    cout << endl;
  }
}