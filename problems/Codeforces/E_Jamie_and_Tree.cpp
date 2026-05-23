#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct Node {
  ll tot = 0;
  int size = 1;
};

struct Tag {
  ll add = 0; // add X to each element in this range
};

// support range add and range sum
struct LazySeg {
  int n;
  vector<Node> tree;
  vector<Tag> lazy;

  LazySeg(const vector<int>& A) {
    n = A.size();
    tree.resize(4 * n);
    lazy.resize(4 * n);
    _build(1, 0, n - 1, A);
  }

  void _pull(int nodeI) {
    tree[nodeI] = agg(tree[2 * nodeI], tree[2 * nodeI + 1]);
  }

  Node agg(Node& left, Node& right) {
    return {left.tot + right.tot, left.size + right.size};
  }

  void _build(int nodeI, int tl, int tr, const vector<int>& A) {
    if (tl == tr) {
      tree[nodeI] = {A[tl], 1};
      return;
    }
    int tm = (tl + tr) / 2;
    _build(2 * nodeI, tl, tm, A);
    _build(2 * nodeI + 1, tm + 1, tr, A);
    _pull(nodeI);
  }

  Node query(int l, int r) {
    return _query(1, 0, n - 1, l, r);
  }

  Tag compose(Tag& old, Tag& newTag) {
    return {old.add + newTag.add};
  }

  void applyTagAndCompose(int nodeI, Tag& t) {
    Node& node = tree[nodeI];
    ll gain = t.add * node.size;
    node.tot += gain;
    lazy[nodeI] = compose(lazy[nodeI], t);
    return;
  }

  void pushDownAndClear(int nodeI) {
    applyTagAndCompose(2 * nodeI, lazy[nodeI]);
    applyTagAndCompose(2 * nodeI + 1, lazy[nodeI]);
    lazy[nodeI] = {0};
  }

  Node _query(int nodeI, int tl, int tr, int ql, int qr) {
    // fully in range
    if (ql <= tl && qr >= tr) {
      return tree[nodeI];
    }
    pushDownAndClear(nodeI);
    int tm = (tl + tr) / 2;
    if (qr <= tm) {
      Node left = _query(2 * nodeI, tl, tm, ql, qr);
      return left;
    } else if (ql >= tm + 1) {
      Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
      return right;
    }
    Node left = _query(2 * nodeI, tl, tm, ql, qr);
    Node right = _query(2 * nodeI + 1, tm + 1, tr, ql, qr);
    return agg(left, right);
  }

  void addRange(int l, int r, ll gain) {
    _addRange(1, 0, n - 1, l, r, gain);
  }

  void _addRange(int nodeI, int tl, int tr, int ql, int qr, ll gain) {
    // fully inside
    if (ql <= tl && qr >= tr) {
      Tag t = {gain};
      applyTagAndCompose(nodeI, t);
      return;
    }
    // disjoint
    if (qr < tl || ql > tr) {
      return;
    }

    pushDownAndClear(nodeI);
    int tm = (tl + tr) / 2;
    _addRange(2 * nodeI, tl, tm, ql, qr, gain);
    _addRange(2 * nodeI + 1, tm + 1, tr, ql, qr, gain);
    _pull(nodeI);
  }

};

struct Lift {
  vector<vector<int>> children;
  vector<vector<int>> lift; // lift[power][node] = that ancestor
  vector<int> depths;
  int n;
  int LOG;

  Lift(const vector<vector<int>>& _children, int _n) {
    children = _children;
    n = _n;
    LOG = 32 - __builtin_clz(n);
    _build();
  }

  void _build() {
    depths.assign(n + 1, 0);
    lift.resize(LOG);
    for (int i = 0; i < LOG; i++) lift[i].assign(n + 1, 0);
    for (int node = 1; node <= n; node++) {
      for (auto child : children[node]) {
        lift[0][child] = node;
      }
    }
    for (int p = 1; p < LOG; p++) {
      for (int node = 1; node <= n; node++) {
        int half = lift[p-1][node];
        if (half == 0) {
          lift[p][node] = 0;
        } else {
          int full = lift[p-1][half];
          lift[p][node] = full;
        }
      }
    }

    // set depths
    auto dfs = [&](auto&& self, int node, int currDepth) -> void {
      depths[node] = currDepth;
      for (auto child : children[node]) {
        self(self, child, currDepth + 1);
      }
    };
    dfs(dfs, 1, 0);
  }

  int kthAncestor(int node, int k) {
    int curr = node;
    for (int b = 0; b < LOG; b++) {
      if ((1 << b) & k) {
        curr = lift[b][curr];
      }
      if (curr == 0) return 0;
    }
    return curr;
  }

  int lca(int a, int b) {
    if (depths[a] < depths[b]) {
      swap(a, b);
    }
    int diff = depths[a] - depths[b];
    a = kthAncestor(a, diff);
    if (a == b) return a;
    for (int bit = LOG - 1; bit >= 0; bit--) {
      int upA = lift[bit][a];
      int upB = lift[bit][b];
      if (upA != upB) {
        a = upA;
        b = upB;
      }
    }
    return lift[0][a];
  }

  int steiner(int a, int b, int c) {
    return lca(a, b) ^ lca(a, c) ^ lca(b, c);
  }


};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, q; cin >> n >> q;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
      int a, b; cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }
    vector<vector<int>> children(n + 1);
    vector<int> depths(n + 1, 0);
    auto makeChildren = [&](auto&& self, int node, int parent, int currDepth) -> void {
      depths[node] = currDepth;
      for (auto adjN : adj[node]) {
        if (adjN == parent) continue;
        children[node].push_back(adjN);
        self(self, adjN, node, currDepth + 1);
      }
    };
    makeChildren(makeChildren, 1, 0, 0);

    int timer = 0;
    vector<int> order; // order of node labels
    vector<int> tin(n + 1); // tin[node] -> time it appears in order
    vector<int> tout(n + 1);
    auto dfs = [&](auto&& self, int node) -> void {
      tin[node] = timer++;
      order.push_back(node);
      for (auto child : children[node]) {
        self(self, child);
      }
      tout[node] = timer;
    };
    dfs(dfs, 1);

    vector<int> vals;
    for (int i = 0; i < n; i++) {
      vals.push_back(A[order[i] - 1]);
    }

    LazySeg seg(vals);
    Lift lift(children, n);

    int R = 1; // current root
    for (int i = 0; i < q; i++) {
      int qtype; cin >> qtype;
      if (qtype == 1) {
        int newRoot; cin >> newRoot;
        R = newRoot;
      } else if (qtype == 2) {
        int a, b; ll gain; cin >> a >> b >> gain;
        // int lca = lift.lca(a, b);
        int lca = lift.steiner(a, b, R);
        // case 1, R == lca
        // then we range add to the whole tree
        if (R == lca) {
          seg.addRange(0, n - 1, gain);
        }

        // case 2, R is outside lca's subtree
        else if (tin[R] < tin[lca] || tin[R] >= tout[lca]) {
          seg.addRange(tin[lca], tout[lca] - 1, gain);
        }

        // case 3, R is inside lca's subtree
        else {
          seg.addRange(0, n - 1, gain);
          int depthR = depths[R];
          int depthLca = depths[lca];
          int jumps = depthR - depthLca - 1;
          int nodeTowards = lift.kthAncestor(R, jumps);
          seg.addRange(tin[nodeTowards], tout[nodeTowards] - 1, -1 * gain);
        }
      } else if (qtype == 3) {
        int v; cin >> v;
        // again 3 cases
        // case 1, R == v
        if (R == v) {
          cout << seg.query(0, n - 1).tot << '\n';
        }
        // case 2, R is outside v's subtree
        else if (tin[R] < tin[v] || tin[R] >= tout[v]) {
          cout << seg.query(tin[v], tout[v] - 1).tot << '\n';
        }
        // case 3, R is inside v's subtree
        else {
          int depthR = depths[R];
          int depthLca = depths[v];
          int jumps = depthR - depthLca - 1;
          int nodeTowards = lift.kthAncestor(R, jumps);
          ll total = seg.query(0, n - 1).tot;
          total -= seg.query(tin[nodeTowards], tout[nodeTowards] - 1).tot;
          cout << total << '\n';
        }
      }
    }
}