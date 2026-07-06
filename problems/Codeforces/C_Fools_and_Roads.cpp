#include <bits/stdc++.h>
using namespace std;

#include <bits/stdc++.h>
using namespace std;

// uses vectors, so max node label cannot be large (1e9)
// unweighted tree

// ⚠️ might be missing functions
// ⚠️ untested
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
  int n;
  cin >> n;
  vector<vector<int>> adj(n + 1);
  map<pair<int,int>,int> edgeToIdx; // [(a, b) -> idx], a < b
  for (int i = 0; i < n - 1; i ++) {
    int a, b;
    cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
    edgeToIdx[{min(a,b),max(a,b)}] = i;
  }

  Lift lift = Lift(1, n, n, adj);
  vector<int> sweep(n + 1); // how many paths pass up through this node
  int k;
  cin >> k;
  for (int i = 0; i < k; i++) {
    int a, b;
    cin >> a >> b;
    if (a == b) continue;
    int ab = lift.lca(a, b);
    sweep[a]++;
    sweep[b]++;
    sweep[ab] -= 2;
  }
  vector<int> edgeVisitResult(n-1); // 0, 1, ... n-2

  function<int(int,int)> dfs = [&](int node, int parent) {
    int pathsUpThroughThisNode = 0;
    for (auto child : adj[node]) {
      if (child == parent) continue;
      pathsUpThroughThisNode += dfs(child, node);
    }
    pathsUpThroughThisNode += sweep[node];
    if (parent != -1) {
      int edgeIdx = edgeToIdx[{min(node,parent),max(node,parent)}];
      edgeVisitResult[edgeIdx] = pathsUpThroughThisNode;
    }
    return pathsUpThroughThisNode;
  };
  dfs(1, -1);
  for (auto v : edgeVisitResult) cout << v << " ";
}





// LAZY HLD SOLUTION BELOW 



// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;


// // EXAMPLE
// // using RawEdgeVal = int; // the raw edge value input, could also be a struct

// // // Accumulated edge data, for instance total edge weight across edges, could be a `using` too instead of struct
// // struct EdgeData {
// //     int total;
// // };

// // // Maps the raw edge value to our EdgeData
// // auto base = [](RawEdgeVal v) -> EdgeData {
// //     return EdgeData{v};
// // };

// // // How to aggregate two EdgeData nodes
// // auto mergeFn = [](EdgeData A, EdgeData B) -> EdgeData {
// //     return EdgeData{A.total + B.total};
// // };

// // // The lazy data each node stores, could be a `using` too
// // struct LazyTag {
// //     int pendingAdd;
// // };

// // // How to apply a lazy update to an EdgeData
// // auto applyLazy = [](LazyTag lazy, EdgeData edgeData) -> EdgeData {
// //     return EdgeData{edgeData.total + lazy.pendingAdd};
// // };

// // // How to combine two lazies
// // auto composeLazies = [](LazyTag a, LazyTag b) -> LazyTag {
// //     return LazyTag{a.pendingAdd + b.pendingAdd};
// // };


// // TO CREATE THE HLD (O(n) build time)
// // RawEdgeVal, EdgeData, LazyTag are the types
// // edges should be vector<pair<int,int>> with node labels (either 0...n-1, or 1...n)
// // vals[node] is the edge ABOVE that node, if we are using root=1, then vals[0] can be whatever dummy value
// // 1 at the end is the root, it can be any value in the tree, separate from if the nodes are 0...n-1 or 1...n
// // last param is `zeroIndexed`, so false means the nodes are 1...n
// // LazyHLDEdge<RawVal, EdgeData, LazyTag> hld(edges, vals, base, mergeFn, applyLazy, composeLazies, 1, false);


// // METHODS

// // O(logN)
// // pointSet(nodeLabel, RawEdgeVal) -> overwrites the edge above `nodeLabel` with this new raw value

// // O(logN)
// // pointApply(nodeLabel, LazyTag) -> directly apply a lazy update to the edge above `nodeLabel`

// // O(log^2 N)
// // pathApply(a, b, LazyTag) -> applies this lazy update to the entire path a...b

// // O(log^2 N)
// // pathQuery(a, b) -> EdgeData, gives us the aggregated data on the path a...b, crashes if a==b

// // O(log N)
// // subtreeApply(nodeLabel, LazyTag) -> applies this update to all edges in the subtree of nodeLabel, no-op if a leaf

// // O(log N)
// // subtreeQuery(nodeLabel) -> EdgeData, gives us the aggregated data of all edges in the subtree, crashes if a leaf

// template <typename RawT, typename StoredT, typename LazyT>
// struct LazyHLDEdge {
//     int n, root, arrSize;
//     bool zeroIndexed;
//     function<StoredT(RawT)> base;
//     function<StoredT(StoredT, StoredT)> combine;
//     function<StoredT(LazyT, StoredT)> applyLazy;
//     function<LazyT(LazyT, LazyT)> composeLazies;
//     vector<vector<int>> adj;
//     vector<int> par, depth, sz, heavy, head, pos;
//     int segN, LOG;
//     vector<optional<StoredT>> tree;
//     vector<optional<LazyT>> lazy;

//     LazyHLDEdge(
//         const vector<pair<int,int>>& edges,
//         const vector<RawT>& vals,
//         function<StoredT(RawT)> base,
//         function<StoredT(StoredT, StoredT)> combine,
//         function<StoredT(LazyT, StoredT)> applyLazy,
//         function<LazyT(LazyT, LazyT)> composeLazies,
//         int root,
//         bool zeroIndexed)
//         : n((int)edges.size() + 1), root(root),
//           arrSize(zeroIndexed ? (int)edges.size() + 1 : (int)edges.size() + 2), zeroIndexed(zeroIndexed),
//           base(base), combine(combine), applyLazy(applyLazy), composeLazies(composeLazies),
//           adj(arrSize), par(arrSize, -1), depth(arrSize, 0), sz(arrSize, 1),
//           heavy(arrSize, -1), head(arrSize, 0), pos(arrSize, 0)
//     {
//         // root must be a real node for the chosen mode (caught only with -DDEBUG / asserts on)
//         assert(zeroIndexed ? (root >= 0 && root < n) : (root >= 1 && root <= n));
//         for (auto& [u, v] : edges) {
//             adj[u].push_back(v);
//             adj[v].push_back(u);
//         }
//         _dfsInit();
//         _dfsDecompose();
//         segN = 1;
//         while (segN < max(n, 1)) segN <<= 1;
//         LOG = max(1, __lg(segN));
//         tree.assign(2 * segN, nullopt);
//         lazy.assign(segN, nullopt);
//         int lo = zeroIndexed ? 0 : 1;
//         int hi = zeroIndexed ? n : n + 1;   // exclusive
//         for (int i = lo; i < hi; i++) {
//             if (i == root) tree[segN + pos[i]] = nullopt;   // no edge above root
//             else tree[segN + pos[i]] = base(vals[i]);
//         }
//         for (int i = segN - 1; i >= 1; i--) {
//             tree[i] = _combineOpt(tree[2*i], tree[2*i+1]);
//         }
//     }

//     optional<StoredT> _combineOpt(const optional<StoredT>& a, const optional<StoredT>& b) {
//         if (!a.has_value()) return b;
//         if (!b.has_value()) return a;
//         return combine(*a, *b);
//     }

//     void _dfsInit() {
//         vector<int> order;
//         order.reserve(n);
//         vector<tuple<int,int,int>> stack;
//         stack.push_back({root, -1, 0});
//         while (!stack.empty()) {
//             auto [node, parent, d] = stack.back();
//             stack.pop_back();
//             par[node] = parent;
//             depth[node] = d;
//             order.push_back(node);
//             for (int nxt : adj[node]) {
//                 if (nxt != parent) stack.push_back({nxt, node, d + 1});
//             }
//         }
//         for (int i = (int)order.size() - 1; i >= 0; i--) {
//             int node = order[i];
//             int best = 0;
//             for (int nxt : adj[node]) {
//                 if (nxt == par[node]) continue;
//                 sz[node] += sz[nxt];
//                 if (sz[nxt] > best) {
//                     best = sz[nxt];
//                     heavy[node] = nxt;
//                 }
//             }
//         }
//     }

//     void _dfsDecompose() {
//         int timer = 0;
//         vector<pair<int,int>> stack;
//         stack.push_back({root, root});
//         while (!stack.empty()) {
//             auto [node, h] = stack.back();
//             stack.pop_back();
//             head[node] = h;
//             pos[node] = timer++;
//             for (int nxt : adj[node]) {
//                 if (nxt == par[node] || nxt == heavy[node]) continue;
//                 stack.push_back({nxt, nxt});
//             }
//             if (heavy[node] != -1) {
//                 stack.push_back({heavy[node], h});
//             }
//         }
//     }

//     void _apply(int p, const LazyT& lazyVal) {
//         if (!tree[p].has_value()) return;   // identity slot (root's dummy edge)
//         tree[p] = applyLazy(lazyVal, *tree[p]);
//         if (p < segN) {
//             if (!lazy[p].has_value()) lazy[p] = lazyVal;
//             else lazy[p] = composeLazies(*lazy[p], lazyVal);
//         }
//     }

//     void _push(int p) {
//         if (p < segN && lazy[p].has_value()) {
//             _apply(2*p, *lazy[p]);
//             _apply(2*p+1, *lazy[p]);
//             lazy[p] = nullopt;
//         }
//     }

//     void _pushTo(int p) {
//         for (int s = LOG; s >= 1; s--) _push(p >> s);
//     }

//     void _pullFrom(int p) {
//         for (p >>= 1; p > 0; p >>= 1) {
//             auto newVal = _combineOpt(tree[2*p], tree[2*p+1]);
//             if (lazy[p].has_value() && newVal.has_value()) {
//                 newVal = applyLazy(*lazy[p], *newVal);
//             }
//             tree[p] = newVal;
//         }
//     }

//     void _segUpdate(int l, int r, const LazyT& lazyVal) {
//         if (l > r) return;
//         l += segN;
//         r += segN + 1;
//         int l0 = l, r0 = r;
//         _pushTo(l0);
//         _pushTo(r0 - 1);
//         int ll = l, rr = r;
//         while (ll < rr) {
//             if (ll & 1) { _apply(ll, lazyVal); ll++; }
//             if (rr & 1) { rr--; _apply(rr, lazyVal); }
//             ll >>= 1; rr >>= 1;
//         }
//         _pullFrom(l0);
//         _pullFrom(r0 - 1);
//     }

//     optional<StoredT> _segQuery(int l, int r) {
//         if (l > r) return nullopt;
//         l += segN;
//         r += segN + 1;
//         _pushTo(l);
//         _pushTo(r - 1);
//         optional<StoredT> resL = nullopt, resR = nullopt;
//         while (l < r) {
//             if (l & 1) { resL = _combineOpt(resL, tree[l]); l++; }
//             if (r & 1) { r--; resR = _combineOpt(tree[r], resR); }
//             l >>= 1; r >>= 1;
//         }
//         return _combineOpt(resL, resR);
//     }

//     void _segPointSet(int idx, const optional<StoredT>& newData) {
//         int p = idx + segN;
//         _pushTo(p);
//         tree[p] = newData;
//         for (p >>= 1; p > 0; p >>= 1) {
//             auto newVal = _combineOpt(tree[2*p], tree[2*p+1]);
//             if (lazy[p].has_value() && newVal.has_value()) {
//                 newVal = applyLazy(*lazy[p], *newVal);
//             }
//             tree[p] = newVal;
//         }
//     }

//     void pointSet(int node, RawT rawVal) {
//         _segPointSet(pos[node], base(rawVal));
//     }

//     void pointApply(int node, LazyT lazyVal) {
//         int p = pos[node];
//         _segUpdate(p, p, lazyVal);
//     }

//     void pathApply(int a, int b, LazyT lazyVal) {
//         while (head[a] != head[b]) {
//             if (depth[head[a]] < depth[head[b]]) swap(a, b);
//             _segUpdate(pos[head[a]], pos[a], lazyVal);
//             a = par[head[a]];
//         }
//         if (depth[a] > depth[b]) swap(a, b);
//         if (pos[a] + 1 <= pos[b])
//             _segUpdate(pos[a] + 1, pos[b], lazyVal);   // skip LCA's parent edge
//     }

//     void subtreeApply(int node, LazyT lazyVal) {
//         if (sz[node] > 1)
//             _segUpdate(pos[node] + 1, pos[node] + sz[node] - 1, lazyVal);
//     }

//     // precondition: a != b (at least one edge on the path). derefs internally.
//     StoredT pathQuery(int a, int b) {
//         optional<StoredT> res = nullopt;
//         while (head[a] != head[b]) {
//             if (depth[head[a]] < depth[head[b]]) swap(a, b);
//             res = _combineOpt(res, _segQuery(pos[head[a]], pos[a]));
//             a = par[head[a]];
//         }
//         if (depth[a] > depth[b]) swap(a, b);
//         if (pos[a] + 1 <= pos[b])
//             res = _combineOpt(res, _segQuery(pos[a] + 1, pos[b]));
//         return *res;
//     }

//     // precondition: node has >= 1 edge in its subtree (not a leaf). derefs internally.
//     StoredT subtreeQuery(int node) {
//         return *_segQuery(pos[node] + 1, pos[node] + sz[node] - 1);
//     }
// };


// using namespace std;
// using ll = long long;

// using RawVal = int;

// struct EdgeData {
//     int tot;
// };

// struct LazyTag {
//     int pendingAdd;
// };

// auto base = [](RawVal v) -> EdgeData {
//     return EdgeData{v};
// };

// auto mergeFn = [](EdgeData A, EdgeData B) -> EdgeData {
//     return EdgeData{A.tot + B.tot};
// };

// auto applyLazy = [](LazyTag lazy, EdgeData edgeData) -> EdgeData {
//     return EdgeData{edgeData.tot + lazy.pendingAdd};
// };

// auto composeLazies = [](LazyTag a, LazyTag b) -> LazyTag {
//     return LazyTag{a.pendingAdd + b.pendingAdd};
// };



// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n; cin >> n;
//     vector<pair<int,int>> edges;
//     for (int i = 0; i < n - 1; i++) {
//         int a, b; cin >> a >> b;
//         edges.push_back({a, b});
//     }

//     vector<int> vals(n + 1, 0);

//     int k; cin >> k;
//     LazyHLDEdge<RawVal, EdgeData, LazyTag> hld(edges, vals, base, mergeFn, applyLazy, composeLazies, 1, false);
//     for (int i = 0; i < k; i++) {
//         int a, b; cin >> a >> b;
//         hld.pathApply(a, b, LazyTag{1});
//     }

//     for (auto& [a, b] : edges) {
//         auto out = hld.pathQuery(a, b);
//         cout << out.tot << " ";
//     }
// }