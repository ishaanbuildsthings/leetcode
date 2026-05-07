#include <bits/stdc++.h>
using namespace std;
using ll = long long;
 
struct LazySegTree {
  int n;
  vector<long long> t, lz;
 
  LazySegTree() {}
  LazySegTree(const vector<long long>& a) { init(a); }
 
  void init(const vector<long long>& a) {
    n = (int)a.size();
    t.assign(4*n, 0);
    lz.assign(4*n, 0);
    build(1, 0, n-1, a);
  }
 
  void build(int v, int tl, int tr, const vector<long long>& a) {
    if (tl == tr) { t[v] = a[tl]; return; }
    int tm = (tl + tr) >> 1;
    build(v<<1, tl, tm, a);
    build(v<<1|1, tm+1, tr, a);
    t[v] = t[v<<1] + t[v<<1|1];
  }
 
  void apply(int v, int tl, int tr, long long x) {
    t[v] += x * (tr - tl + 1);
    lz[v] += x;
  }
 
  void push(int v, int tl, int tr) {
    if (!lz[v] || tl == tr) return;
    int tm = (tl + tr) >> 1;
    apply(v<<1, tl, tm, lz[v]);
    apply(v<<1|1, tm+1, tr, lz[v]);
    lz[v] = 0;
  }
 
  void rangeAdd(int l, int r, long long x) { rangeAdd(1, 0, n-1, l, r, x); }
  void rangeAdd(int v, int tl, int tr, int l, int r, long long x) {
    if (r < tl || tr < l) return;
    if (l <= tl && tr <= r) { apply(v, tl, tr, x); return; }
    push(v, tl, tr);
    int tm = (tl + tr) >> 1;
    rangeAdd(v<<1, tl, tm, l, r, x);
    rangeAdd(v<<1|1, tm+1, tr, l, r, x);
    t[v] = t[v<<1] + t[v<<1|1];
  }
 
  long long rangeSum(int l, int r) { return rangeSum(1, 0, n-1, l, r); }
  long long rangeSum(int v, int tl, int tr, int l, int r) {
    if (r < tl || tr < l) return 0;
    if (l <= tl && tr <= r) return t[v];
    push(v, tl, tr);
    int tm = (tl + tr) >> 1;
    return rangeSum(v<<1, tl, tm, l, r) + rangeSum(v<<1|1, tm+1, tr, l, r);
  }
};
 
 
int main() {
  int n, q; cin >> n >> q;
  vector<int> values(n + 1); // maps node label -> node value
  for (int i = 0; i < n; i++) cin >> values[i + 1];
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  int timer = 0;
  vector<int> tin(n + 1); // tin[node] is the entry
  vector<int> tout(n + 1); // tout[node] is the exit
  vector<ll> order; // order[time] is the node's VALUE
 
  function<void(int,int)> dfs = [&](int node, int parent) {
    tin[node] = timer;
    order.push_back(values[node]);
    for (auto child : adj[node]) {
      if (child != parent) {
        timer++;
        dfs(child, node);
      }
    }
    tout[node] = timer;
  };
  dfs(1, -1);
 
  LazySegTree seg = LazySegTree(order);
  for (int i = 0; i < q; i++) {
    int op; cin >> op;
    if (op == 1) {
      int s, x; cin >> s >> x;
      int idx = tin[s];
      ll oldVal = seg.rangeSum(idx, idx);
      seg.rangeAdd(idx, idx, x - oldVal);
    } else {
      int s; cin >> s;
      cout << seg.rangeSum(tin[s], tout[s]) << "\n";
    }
  }
}