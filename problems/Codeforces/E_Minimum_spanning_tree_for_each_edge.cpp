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

  int find(int a) {
    if (p[a] == a) return a;
    return p[a] = find(p[a]);
  }

  bool unite(int a, int b) {
    int l1 = find(a), l2 = find(b);
    if (l1 == l2) return false;
    int s1 = sz[l1], s2 = sz[l2];
    if (s1 > s2) swap(l1, l2);
    sz[l2] += sz[l1];
    p[l1] = l2;
    return true;
  }

  bool same(int a, int b) {
    return find(a) == find(b);
  }
};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m;
  cin >> n >> m;
  DSU dsu = DSU(n);
  vector<array<int,3>> es;
  for (int i = 0; i < m; i++) {
    int a, b, w;
    cin >> a >> b >> w;
    es.push_back({w, a, b});
  }
  vector<array<int,3>> orig = es;
  sort(es.begin(), es.end());
  vector<array<int,3>> treeEdges;
  long long mstSum = 0;
  for (auto [w, a, b] : es) {
    if (!dsu.same(a, b)) {
      dsu.unite(a, b);
      mstSum += w;
      treeEdges.push_back({w, a, b});
    }
  }
  vector<vector<pair<int,int>>> edges(n + 1); // edges[node] -> {adjNode, weight}
  for (auto [w, a, b] : treeEdges) {
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
    depths[node] = node == 1 ? 0 : depths[parent] + 1;

    // fill this nodes up and mx
    for (int k = 1; k < LOG; k++) {
      int midNode = up[k-1][node];
      int upUp = up[k-1][midNode];
      up[k][node] = upUp;
      mx[k][node] = max(mx[k-1][node], mx[k-1][midNode]);
    }

    for (auto [adjNode, adjW] : edges[node]) {
      if (adjNode == parent) continue;
      dfs(adjNode, node, adjW);
    }
  };
  dfs(1, 1, 0); // 1s parent is 1

  function<int(int,int)> mxOnPath = [&](int a, int b) {
    int res = 0;
    // lift deeper node to same level
    if (depths[a] < depths[b]) swap(a, b); // a is under b
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        res = max(res, mx[k][a]);
        a = up[k][a];
      }
    }
    // if same, we are already at lca
    if (a == b) return res;

    // lift both up keeping below LCA, since 2^big power would point to the lca
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

  for (int i = 0; i < m; i++) {
    auto [w, a, b] = orig[i];
    // mst sum, minus the max on that path, plus this edge
    cout << mstSum - mxOnPath(a, b) + w << endl;
  }
}