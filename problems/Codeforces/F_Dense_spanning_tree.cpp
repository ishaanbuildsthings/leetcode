#include <bits/stdc++.h>
using namespace std;

struct DSU {
  vector<int> p;
  vector<int> sz;
  int components;
  DSU(int n) {
    sz.assign(n + 1, 1);
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0);
    components = n;
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
    if (s1 > s2) swap(l1, l2);
    sz[l2] += sz[l1];
    p[l1] = l2;
    components--;
    return true;
  }

  bool same(int a, int b) {
    return find(a) == find(b);
  }

  int comps() {
    return components;
  }
};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m;
  cin >> n >> m;
  vector<array<int,3>> es;
  for (int i = 0; i < m; i++) {
    int a, b, w;
    cin >>a>>b>>w;
    es.push_back({w, a, b});
  }
  sort(es.begin(), es.end());

  long long res = 1000000000000;

  // for each edge, we make a new DSU and merge to the right until we cannot go

  for (int i = 0; i < m; i++) {
    DSU dsu = DSU(n);
    auto [iw, _, __] = es[i];
    for (int j = i; j < m; j++) {
      auto [w, a, b] = es[j];
      dsu.unite(a, b);
      if (dsu.comps() == 1) {
        res = min(res, (long long)(w - iw));
        break;
      }
    }
  }

  if (res == 1000000000000) {
    cout << "NO" << endl;
  } else {
    cout << "YES" << endl;
    cout << res << endl;
  }
}