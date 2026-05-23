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

#include <bits/stdc++.h>
using namespace std;

// uses vectors, so max node label cannot be large (1e9)
// unweighted tree

// ⚠️ might be missing functions
// ⚠️ untested
// ⚠️ only for edges
// ⚠️ might not have a destruct / cleanup for multiple test cases
// ⚠️ prob other stuff too lol

struct Lift {
  int numNodes, LOG, root; // label of root
  vector<int> depths;
  vector<vector<int>> adj; // adj[node] is a list of adjacent nodes in the graph
  vector<vector<int>> up;

  Lift(int root, int numNodes, int maxNodeLabel, const vector<vector<int>>& adj) : numNodes(numNodes), root(root), adj(adj) {
    depths.resize(maxNodeLabel + 1);
    LOG = 32 - __builtin_clz(numNodes);
    up.assign(LOG, vector<int>(maxNodeLabel + 1)); // up[power][node]

    function<void(int,int)> dfs = [&](int node, int parent) {
      depths[node] = node == root ? 0 : depths[parent] + 1;
      up[0][node] = parent;
      for (int k = 1; k < LOG; k++) {
        int mid = up[k-1][node];
        up[k][node] = up[k-1][mid];
      }
      for (auto child : adj[node]) {
        if (child == parent) continue;
        dfs(child, node);
      }
    };
    dfs(root, root); // root points to itself
  }

  // O(logN) - get Kth ancestor of a node, or root if overshooting
  int kthAncestor(int a, int kth) {
    for (int k = 0; k < LOG; k++) if (kth >> k & 1) a = up[k][a];
    return a;
  }

  // O(logN) - get the LCA of two nodes when rooted at `root`
  int lca(int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    for (int k = 0; k < LOG; k++) if (diff >> k & 1) a = up[k][a]; // lift to same level
    if (a == b) return a;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        a = up[k][a];
        b = up[k][b];
      }
    }
    return up[0][a];
  }

  // O(logN) - get the edge path distance from a<>b
  int pathDist(int a, int b) {
    int ab = lca(a, b);
    return depths[a] + depths[b] - 2 * depths[ab];
  }

  // O(logN) - find the unique node on all three pairs of simple paths
  int geodesic(int a, int b, int c) {
    return lca(a, b) ^ lca(a, c) ^ lca(b, c); // can also find deepest LCA, or LCA that isn't the other 2 LCAs
  }

  // O(logN) - find the kth node on the path from a->b, 1st node would be a. If we overshoot, return -1
  int kthOnPath(int a, int b, int kth) {
    int ab = lca(a, b);
    int distAToAB = depths[a] - depths[ab];
    int distBToAB = depths[b] - depths[ab];
    int totalLen = distAToAB + distBToAB + 1;
    if (kth < 1 || kth > totalLen) return -1;
    if (kth <= distAToAB + 1) return kthAncestor(a, kth - 1);
    int past = kth - (distAToAB + 1);
    return kthAncestor(b, distBToAB - past);
  }

  // O(logN) - find the closest distance from x to the path a<>b
  int distToPath(int a, int b, int x) {
    int geo = geodesic(a, b, x); // can also do dist(a, x) + dist(b, x) - dist(a, b) / 2 to avoid geodesic
    return pathDist(geo, x);
  }

  // O(logN) - checks if x exists on the path a<>b
  bool inPath(int a, int b, int x) {
    return geodesic(a, b, x) == x; // can also check if pathDist(a, x) + pathDist(x, b) == pathDist(a, b), or check pathDist(x, geo) == 0
  }
};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q; cin >> n >> q;
  vector<ll> values(n);
  vector<ll> treeVals;
  for (int i = 0; i < n; i++) cin >> values[i];
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }


  Lift lift = Lift(1, n, n, adj);

  vector<int> sz(n + 1);
  vector<int> nodeToTime(n + 1);
  ll totot = 0;
  int time = 0;
  function<void(int,int)> dfs = [&](int node, int parent) {
    nodeToTime[node] = time++;
    sz[node] = 1;
    treeVals.push_back(values[node-1]);
    totot += values[node];
    for (auto child : adj[node]) {
      if (child == parent) continue;
      dfs(child, node);
      sz[node] += sz[child];
    }
  };
  dfs(1, -1);
  LazySegTree seg = LazySegTree(treeVals);

  function<pair<int,int>(int)> nodeToLR = [&](int node) {
    int idx = nodeToTime[node];
    int right = idx + sz[node] - 1;
    return make_pair(idx, right);
  };

  // in general we need to add to everything, except for some path geodesic -> root path
  // if that path points up (when rooted at 1), we just add to gedesics subtree
  // if that path points down, we could add to all, and subtract from the down
  int currRoot = 1;
  for (int i = 0; i < q; i++) {
    int op; cin >> op;
    if (op == 1) {
      int newRoot; cin >> newRoot;
      currRoot = newRoot;
    } else if (op == 2) {
      int a, b, x; cin >> a >> b >> x;
      int geo = lift.geodesic(a, b, currRoot);
      if (geo == currRoot) {
        seg.rangeAdd(0, n - 1, x);
        // add to the entire tree
        continue;
      }
      int nxt = lift.kthOnPath(geo, currRoot, 2);
      // if we are pointing up
      if (lift.depths[nxt] < lift.depths[geo]) {
        auto [l, r] = nodeToLR(geo);
        // cout << "l: " << l << " r: " << r << endl;
        seg.rangeAdd(l, r, x);
        // add to geodesic subtree
      } else {
        // if we are pointing down, add to all and subtract from down
        seg.rangeAdd(0, n - 1, x);
        auto [l, r] = nodeToLR(nxt);
        seg.rangeAdd(l, r, -x);
      }
    } else {
      int subtree; cin >> subtree;
      // we need the total sum of everything, except subtree -> root filled area
      // if subtree is the root, we return entire sum
      ll ans;
      if (subtree == currRoot) {
        ans = seg.rangeSum(0, n - 1);
      } else {
        // if that edge is pointing up, we just get the subtree sum
        int nxt = lift.kthOnPath(subtree, currRoot, 2);
        if (lift.depths[nxt] < lift.depths[subtree]) {
          auto [l, r] = nodeToLR(subtree);
          ans = seg.rangeSum(l, r);
        } else {
          // if we exclude a pointing down region, we get the sum of everything minus that down region
          ans = seg.rangeSum(0, n - 1);
          auto [l, r] = nodeToLR(nxt);
          ans -= seg.rangeSum(l, r);
        }
      }
      cout << ans << endl;
    }
  }


}