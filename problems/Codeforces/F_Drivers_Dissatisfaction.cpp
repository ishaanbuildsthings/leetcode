#include <bits/stdc++.h>
using namespace std;

// ⚠️ not constant optimized, using recursive leader function
// ⚠️ probably missing methods
// ⚠️ missing functionalities like min or max of a group, could have a few templates for those
// ⚠️ missign complexity comments above functions
// ⚠️ can't support different groups of nodes, only works for 1...n basically, or 0...n-1
// ✅ passed https://codeforces.com/edu/course/2/lesson/7/1/practice/contest/289390/problem/D

#include <bits/stdc++.h>
using namespace std;

struct Edge {
  int a, b, idx, w, c;
  bool inMst = false;
};

struct DSU {
  int n;
  vector<int> p, sz; // parents, size of leader

  DSU(int n) {
    p.resize(n + 1);
    iota(p.begin(), p.end(), 0); // nodes are numbered 0 to n-1
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

#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// uses vectors, so max node label cannot be large (1e9)
// unweighted tree

// ⚠️ might be missing functions
// ⚠️ untested
// ⚠️ might not have a destruct / cleanup for multiple test cases
// ⚠️ prob other stuff too lol
// ⚠️ also has mx and mn which might make it slow if those are not needed

struct Lift {
  int numNodes, LOG, root; // label of root
  int INF = 2000000000;
  vector<int> depths;
  vector<vector<Edge>> adj; // adj[node] -> [Edge, ...]
  vector<vector<int>> up;
  vector<vector<ll>> upWeight;
  vector<vector<int>> mx; // mx[power][node] is the max weight on that lift
  vector<vector<int>> mn;
  vector<vector<int>> mxId;

  Lift(int root, int numNodes, int maxNodeLabel, const vector<vector<Edge>>& adj) : numNodes(numNodes), root(root), adj(adj) {
    depths.resize(maxNodeLabel + 1);
    LOG = 32 - __builtin_clz(numNodes);
    up.assign(LOG, vector<int>(maxNodeLabel + 1)); // up[power][node]
    mx.assign(LOG, vector<int>(maxNodeLabel + 1));
    mxId.assign(LOG, vector<int>(maxNodeLabel + 1)); // mxId[power][node] = edge idx for max edge
    mn.assign(LOG, vector<int>(maxNodeLabel + 1));
    upWeight.assign(LOG, vector<ll>(maxNodeLabel + 1));


    function<void(int,int,const Edge&)> dfs = [&](int node, int parent, const Edge&e) {
      depths[node] = node == root ? 0 : depths[parent] + 1;
      up[0][node] = parent;
      upWeight[0][node] = (ll)e.w;
      mn[0][node] = node == root ? INF : e.w;
      mx[0][node] = node == root ? -INF : e.w; // otherwise a tree of negative edges gets messed up
      mxId[0][node] = node == root ? -1 : e.idx;
      for (int k = 1; k < LOG; k++) {
        int mid = up[k-1][node];

        up[k][node] = up[k-1][mid];

        ll wToMid = upWeight[k-1][node];
        upWeight[k][node] = wToMid + upWeight[k-1][mid];

        int mxToMid = mx[k-1][node];
        mx[k][node] = max(mxToMid, mx[k-1][mid]);

        int mnToMid = mn[k-1][node];
        mn[k][node] = min(mnToMid, mn[k-1][mid]);

        int mxIdToMid = mxId[k-1][node];
        mxId[k][node] = mxToMid >= mx[k-1][mid] ? mxIdToMid : mxId[k-1][mid];
      }
      for (auto &e2 : adj[node]) {
        if (e.idx == e2.idx) continue;
        int to = e2.a == node ? e2.b : e2.a;
        dfs(to, node, e2);
      }
    };
    dfs(root, root, Edge{root, root, -1, 0, 0, false}); // root points to itself
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
  int pathDistUnweighted(int a, int b) {
    int ab = lca(a, b);
    return depths[a] + depths[b] - 2 * depths[ab];
  }

  // O(logN) - get the weighted path distance from a<>b
  ll pathDistWeighted(int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    ll res = 0;
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        res += upWeight[k][a];
        a = up[k][a];
      }
    }
    if (a == b) return res;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        res += upWeight[k][a] + upWeight[k][b];
        a = up[k][a];
        b = up[k][b];
      }
    }
    return res + upWeight[0][a] + upWeight[0][b];
  }

  // O(logN) - find the unique node on all three pairs of simple paths
  int geodesic(int a, int b, int c) {
    return lca(a, b) ^ lca(a, c) ^ lca(b, c); // can also find deepest LCA, or LCA that isn't the other 2 LCAs
  }

  // O(logN) - find the kth node on the path from a->b, 0th node would be a. If we overshoot, return -1
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
  int unweightedDistToPath(int a, int b, int x) {
    int geo = geodesic(a, b, x); // can also do dist(a, x) + dist(b, x) - dist(a, b) / 2 to avoid geodesic
    return pathDistUnweighted(geo, x);
  }

  // O(logN) - checks if x exists on the path a<>b
  bool inPath(int a, int b, int x) {
    return geodesic(a, b, x) == x; // can also check if pathDist(a, x) + pathDist(x, b) == pathDist(a, b), or check pathDist(x, geo) == 0
  }

  // O(logN) - find the closest weighted distance from x to the path a<>b
  int weightedDistToPath(int a, int b, int x) {
    return 0; // TODO
  }

  // O(logN) - finds the node w weight along from a->b, can overshoot a bit
  int weightOnPath(int a, int b, int w) {
    return 0; // TODO
  }

  // O(logN) - finds the max edge weight on the path a<>b + idx
  pair<int,int> mxOnPath(int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    int res = -INF;
    int mxIdHere = -1;
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        if (mx[k][a] > res) {
          res = mx[k][a];
          mxIdHere = mxId[k][a];
        }
        a = up[k][a];
      }
    }
    if (a == b) return {res, mxIdHere};
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        if (mx[k][a] > res) {
          res = mx[k][a];
          mxIdHere = mxId[k][a];
        }
        if (mx[k][b] > res) {
          res = mx[k][b];
          mxIdHere = mxId[k][b];
        }
        a = up[k][a];
        b = up[k][b];
      }
    }
    if (mx[0][a] > res) {
      res = mx[0][a];
      mxIdHere = mxId[0][a];
    }
    if (mx[0][b] > res) {
      res = mx[0][b];
      mxIdHere = mxId[0][b];
    }
    return {res, mxIdHere};
  }

  // O(logN) - finds the min edge weight on the path a<>b
  int mnOnPath(int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    int res = INF;
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        res = min(res, mn[k][a]);
        a = up[k][a];
      }
    }
    if (a == b) return res;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        res = min(res, min(mn[k][a], mn[k][b]));
        a = up[k][a];
        b = up[k][b];
      }
    }
    return min(res, min(mn[0][a], mn[0][b]));
  }

};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m;
  cin >> n >> m;
  vector<int> dis;
  vector<int> cost;
  vector<Edge> inputRoadsForMst; // holds Edges but sorted in a random order
  for (int i = 0; i < m; i++) {
    int w;
    cin >> w;
    dis.push_back(w);
  }
  for (int i = 0; i < m; i++) {
    int c;
    cin >> c;
    cost.push_back(c);
  }
  for (int i = 0; i < m; i++) {
    int a, b;
    cin >> a >> b;
    Edge e = Edge{a, b, i, dis[i], cost[i], false};
    inputRoadsForMst.push_back(e);
  }
  sort(inputRoadsForMst.begin(), inputRoadsForMst.end(), [](const Edge& a, const Edge& b) {
      return a.w < b.w;
  });

  DSU dsu = DSU(n);
  ll mstTotWeight = 0;
  vector<vector<Edge>> adj(n + 1); // node -> [Edge, ...]
  for (int i = 0; i < (int)inputRoadsForMst.size(); i++) {
    auto &e = inputRoadsForMst[i];
    if (!dsu.same(e.a, e.b)) {
      dsu.unite(e.a, e.b);
      e.inMst = true;
      adj[e.a].push_back(e);
      adj[e.b].push_back(e);
      mstTotWeight += e.w;
    }
  }


  int S;
  cin >> S;

  Lift lift = Lift(1, n, n, adj);
  ll res = 1e18;
  Edge reducedEdge;
  int removedEdgeIdx = -1;

  for (int i = 0; i < (int)inputRoadsForMst.size(); i++) {
    auto e = inputRoadsForMst[i];

    if (e.inMst) {
      // if it is in the MST, we just reduce this as much as we can
      int reduces = S / e.c;
      if (mstTotWeight - reduces < res) {
        res = mstTotWeight - reduces;
        reducedEdge = e;
        removedEdgeIdx = -1;
      }
    } else {
      // if not in the MST, find the most expensive weight on the path that we can evict
      auto [mostExpensive, mostExpensiveIdx] = lift.mxOnPath(e.a, e.b);
      ll newMstTotWeight = mstTotWeight - mostExpensive + e.w;
      int reduces = S / e.c;
      if (newMstTotWeight - reduces < res) {
        res = newMstTotWeight - reduces;
        reducedEdge = e;
        removedEdgeIdx = mostExpensiveIdx;
      }
    }
  }


  cout << res << endl;

  for (auto &e : inputRoadsForMst) {
    if (e.idx == reducedEdge.idx) {
      cout << e.idx + 1 << " " << (e.w - (S / e.c)) << endl;
      continue;
    }
    if (e.idx == removedEdgeIdx) {
      continue;
    }
    if (!e.inMst) continue;
    cout << e.idx + 1 << " " << e.w << endl;
  }
}