#include <bits/stdc++.h>
using namespace std;

struct DSU {
  int n;
  vector<int> p, sz, mn, mx; // parents, size of leader, min of leader, max of leader

  DSU(int n) {
    p.resize(n + 1);
    mn.resize(n + 1);
    mx.resize(n + 1);
    iota(p.begin(), p.end(), 0); // nodes are numbered 0 to n-1
    iota(mn.begin(), mn.end(), 0);
    iota(mx.begin(), mx.end(), 0);
    sz.assign(n + 1, 1);
  }

  int leader(int node) {
    if (p[node] == node) return node;
    return p[node] = leader(p[node]);
  }

  bool unite(int a, int b) {
    int l1 = leader(a);
    int l2 = leader(b);
    if (l1 == l2) return false;
    if (sz[l1] > sz[l2]) swap(l1, l2);
    p[l1] = l2;
    mn[l2] = min(mn[l2], mn[l1]);
    mx[l2] = max(mx[l2], mx[l1]);
    sz[l2] += sz[l1];
    return true;
  }

  bool same(int a, int b) {
    int l1 = leader(a);
    int l2 = leader(b);
    return l1 == l2;
  }

  int size(int node) {
    return sz[leader(node)];
  }

  int getMax(int node) {
    return mx[leader(node)];
  }

  int getMin(int node) {
    return mn[leader(node)];
  }
};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    DSU dsu = DSU(n);
    for (int i = 0; i < m; i++) {
      string op;
      int a, b;
      cin >> op;
      if (op == "union") {
        cin >> a >> b;
        dsu.unite(a, b);
      } else {
        cin >> a;
        cout << dsu.getMin(a) << " " << dsu.getMax(a) << " " <<  dsu.size(a) << " " << endl;
      }
    }
}