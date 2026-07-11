#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct DSU {
  vector<int> p;
  vector<int> sz;
  DSU(int n) {
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0);
    sz.assign(n + 1, 1);
  }

  int find(int a) {
    if (p[a] == a) return a;
    return p[a] = find(p[a]);
  }

  bool unite(int a, int b) {
    int l1 = find(a);
    int l2 = find(b);
    if (l1 == l2) return false;
    int s1 = sz[l1];
    int s2 = sz[l2];
    if (s1 > s2) swap (l1, l2);
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
  vector<array<int,3>> edges;
  for (int i = 0; i < m; i++) {
    int a, b, w;
    cin >>a>>b>>w;
    edges.push_back({w, a, b});
  }
  sort(edges.begin(), edges.end());
  ll res = 0;
  for (auto [w, a, b] : edges) {
    if (dsu.same(a, b)) continue;
    res += w;
    dsu.unite(a, b);
  }
  cout << res;
}