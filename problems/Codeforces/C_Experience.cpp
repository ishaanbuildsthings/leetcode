 
#include <bits/stdc++.h>
using namespace std;

struct DSU {
  vector<int> p, sz, score, offset; // parent[node] and sz[leader], score[leader] is how much we added, offset[node] is the negative offset for node->parent[node] edge

  DSU(int n) {
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0);
    sz.assign(n + 1, 1);
    offset.assign(n + 1, 0);
    score.assign(n + 1, 0);
  }


  pair<int, int> leaderAndSum(int a) {
    if (a == p[a]) return {a, score[a]};
    auto [leader, aboveScore] = leaderAndSum(p[a]);
    return {leader, aboveScore + score[a] + offset[a]};
  }

  bool same(int a, int b) {
    auto [l1,_] = leaderAndSum(a);
    auto [l2,_] = leaderAndSum(b);
    return l1 == l2;
  }

  void add(int node, int amt) {
    auto [leader,_] = leaderAndSum(node);
    score[leader] += amt;
  }

  bool unite(int a, int b) {
    auto [l1,_] = leaderAndSum(a);
    auto [l2,_] = leaderAndSum(b);
    if (l1 == l2) return false;
    int s1 = sz[l1];
    int s2 = sz[l2];
    if (s1 > s2) swap(l1, l2);
    sz[l2] += sz[l1];
    p[l1] = l2;
    offset[l1] -= score[l2];
    return true;
  }

  int getSize(int a) {
    auto [leader,_] = leaderAndSum(a);
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
        cout << sum << endl;
      }
    }
}