#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct SegTreeOR64 {
    using UL = unsigned long long;
    int n;
    vector<UL> st;
    vector<int> lazy;

    SegTreeOR64() : n(0) {}
    SegTreeOR64(const vector<int>& labels) { init(labels); }

    void init(const vector<int>& labels) {
        n = (int)labels.size();
        st.assign(4 * max(1, n), 0);
        lazy.assign(4 * max(1, n), -1);
        if (n) build(1, 0, n - 1, labels);
    }

    void rangeAssign(int l, int r, int label) {
        if (l > r || n == 0) return;
        assign(1, 0, n - 1, l, r, label);
    }

    UL rangeOr(int l, int r) {
        if (l > r || n == 0) return 0ULL;
        return query(1, 0, n - 1, l, r);
    }

    int rangeDifferent(int l, int r) {
        return __builtin_popcountll(rangeOr(l, r));
    }

    void build(int p, int L, int R, const vector<int>& a) {
        if (L == R) {
            st[p] = (UL)1ULL << a[L];
            lazy[p] = -1;
            return;
        }
        int M = (L + R) >> 1;
        build(p << 1, L, M, a);
        build(p << 1 | 1, M + 1, R, a);
        st[p] = st[p << 1] | st[p << 1 | 1];
    }

    void apply(int p, int label) {
        st[p] = (UL)1ULL << label;
        lazy[p] = label;
    }

    void push(int p) {
        if (lazy[p] != -1) {
            int v = lazy[p];
            apply(p << 1, v);
            apply(p << 1 | 1, v);
            lazy[p] = -1;
        }
    }

    void assign(int p, int L, int R, int i, int j, int label) {
        if (j < L || R < i) return;
        if (i <= L && R <= j) { apply(p, label); return; }
        push(p);
        int M = (L + R) >> 1;
        assign(p << 1, L, M, i, j, label);
        assign(p << 1 | 1, M + 1, R, i, j, label);
        st[p] = st[p << 1] | st[p << 1 | 1];
    }

    UL query(int p, int L, int R, int i, int j) {
        if (j < L || R < i) return 0ULL;
        if (i <= L && R <= j) return st[p];
        push(p);
        int M = (L + R) >> 1;
        return query(p << 1, L, M, i, j) | query(p << 1 | 1, M + 1, R, i, j);
    }
};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q; cin >> n >> q;
  vector<int> colors(n + 1);
  for (int i = 1; i <= n; ++i) cin >> colors[i];

  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  vector<int> tin(n + 1);
  vector<int> tout(n + 1);
  vector<int> valuesInOrder; // holds "bitsets" (longs)
  int timer = 0;

  function<void(int, int)> dfs = [&](int node, int parent) {
    tin[node] = timer;
    valuesInOrder.push_back(colors[node]);
    for (auto child : adj[node]) {
      if (child != parent) {
        timer++;
        dfs(child, node);
      }
    }
    tout[node] = timer;
  };
  dfs(1, -1);

  SegTreeOR64 seg = SegTreeOR64(valuesInOrder);

  for (int i = 0; i < q; i++) {
    int op; cin >> op;
    if (op == 1) {
      int node, color; cin >> node >> color;
      seg.rangeAssign(tin[node], tout[node], color);
    } else {
      int node; cin >> node;
      cout << seg.rangeDifferent(tin[node], tout[node]) << "\n";
    }
  }
}