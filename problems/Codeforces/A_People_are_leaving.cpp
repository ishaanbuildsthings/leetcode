 
#include <bits/stdc++.h>
using namespace std;

struct DSU {
  vector<int> right;
  vector<int> sz;
  DSU(int n) {
    sz.assign(n + 1, 1);
    right.resize(n + 1);
    iota(right.begin(), right.end(), 0);
  }

  int find(int node) {
    if (right[node] == -1) return -1;
    if (right[node] == node) return node;
    return right[node] = find(right[node]);
  }

  bool unite(int a, int b) {
    int l1 = find(a);
    int l2 = find(b);
    if (l1 == l2) return false;
    int s1 = sz[l1];
    int s2 = sz[l2];
    if (s1 > s2) swap(l1, l2);
    right[l1] = l2;
    sz[l2] += sz[l1];
    return true;
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
      int v;
      cin >> op >> v;
      if (op == "-") {
        dsu.right[v] = v + 1 <= n ? dsu.right[v + 1] : -1;
      } else {
        cout << dsu.find(v) << endl;
      }
    }
}