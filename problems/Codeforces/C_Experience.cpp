#include <bits/stdc++.h>
using namespace std;

struct DSU {
  vector<int> p, sz, score;

  DSU(int n) {
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0);
    sz.assign(n + 1, 1);
    score.assign(n + 1, 0);
  }

  pair<int, int> leaderAndSum(int a) {
    if (a == p[a]) return {a, score[a]};
    auto [leader, aboveScore] = leaderAndSum(p[a]);
    return {leader, aboveScore + score[a]};
  }

  bool same(int a, int b) {
    auto [l1, _1] = leaderAndSum(a);
    auto [l2, _2] = leaderAndSum(b);
    return l1 == l2;
  }

  void add(int node, int amt) {
    auto [leader, _] = leaderAndSum(node);
    score[leader] += amt;
  }

  bool unite(int a, int b) {
    auto [l1, _1] = leaderAndSum(a);
    auto [l2, _2] = leaderAndSum(b);
    if (l1 == l2) return false;
    if (sz[l1] > sz[l2]) swap(l1, l2);
    sz[l2] += sz[l1];
    p[l1] = l2;
    score[l1] -= score[l2];
    return true;
  }

  int getSize(int a) {
    auto [leader, _] = leaderAndSum(a);
    return sz[leader];
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
      cin >> op;
      if (op == "add") {
        int node, amt;
        cin >> node >> amt;
        dsu.add(node, amt);
      } else if (op == "join") {
        int a, b;
        cin >> a >> b;
        dsu.unite(a, b);
      } else {
        int node;
        cin >> node;
        auto [leader, sum] = dsu.leaderAndSum(node);
        cout << sum << "\n";
      }
    }
}