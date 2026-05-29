#include <bits/stdc++.h>
using namespace std;

struct DSU {
  int n;
  vector<int> p, sz; // parents, size of leader

  DSU(int n) {
    p.resize(n);
    iota(p.begin(), p.end(), 0); // nodes are numbered 0 to n-1
    sz.assign(n, 1);
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
      cin >> op >> a >> b;
      a -= 1;
      b -= 1;
      if (op == "union") {
        dsu.unite(a, b);
      } else {
        if (dsu.same(a, b)) {
          cout << "YES" << endl;
        } else {
          cout << "NO" << endl;
        }
      }
    }
}