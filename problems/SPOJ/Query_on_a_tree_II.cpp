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
  vector<vector<pair<int,int>>> adj; // adj[node] -> [(adjNode, adjW), ...]
  vector<vector<int>> up;
  vector<vector<ll>> upWeight;
  vector<vector<int>> mx; // mx[power][node] is the max weight on that lift
  vector<vector<int>> mn;

  Lift(int root, int numNodes, int maxNodeLabel, const vector<vector<pair<int,int>>>& adj) : numNodes(numNodes), root(root), adj(adj) {
    depths.resize(maxNodeLabel + 1);
    LOG = 32 - __builtin_clz(numNodes);
    up.assign(LOG, vector<int>(maxNodeLabel + 1)); // up[power][node]
    mx.assign(LOG, vector<int>(maxNodeLabel + 1));
    mn.assign(LOG, vector<int>(maxNodeLabel + 1));
    upWeight.assign(LOG, vector<ll>(maxNodeLabel + 1));

    function<void(int,int,int)> dfs = [&](int node, int parent, int wToP) {
      depths[node] = node == root ? 0 : depths[parent] + 1;
      up[0][node] = parent;
      upWeight[0][node] = (ll)wToP;
      mn[0][node] = node == root ? INF : wToP;
      mx[0][node] = node == root ? -INF : wToP; // otherwise a tree of negative edges gets messed up
      for (int k = 1; k < LOG; k++) {
        int mid = up[k-1][node];
        up[k][node] = up[k-1][mid];
        ll wToMid = upWeight[k-1][node];
        upWeight[k][node] = wToMid + upWeight[k-1][mid];
        int mxToMid = mx[k-1][node];
        mx[k][node] = max(mxToMid, mx[k-1][mid]);
        int mnToMid = mn[k-1][node];
        mn[k][node] = min(mnToMid, mn[k-1][mid]);
      }
      for (auto [child, wToChild] : adj[node]) {
        if (child == parent) continue;
        dfs(child, node, wToChild);
      }
    };
    dfs(root, root, 0); // root points to itself
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
    if (distAToAB >= kth) return kthAncestor(a, kth);
    int past = kth - distAToAB;
    int distBToAB = depths[b] - depths[ab];
    if (distBToAB < past) return -1;
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

  // O(logN) - finds the max edge weight on the path a<>b
  int mxOnPath(int a, int b) {
    if (depths[a] < depths[b]) swap(a, b);
    int diff = depths[a] - depths[b];
    int res = -INF;
    for (int k = 0; k < LOG; k++) {
      if (diff >> k & 1) {
        res = max(res, mx[k][a]);
        a = up[k][a];
      }
    }
    if (a == b) return res;
    for (int k = LOG - 1; k >= 0; k--) {
      if (up[k][a] != up[k][b]) {
        res = max(res, max(mx[k][a], mx[k][b]));
        a = up[k][a];
        b = up[k][b];
      }
    }
    return max(res, max(mx[0][a], mx[0][b]));
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
  int t;
  cin >> t;
  while (t--) {
    int n;
    cin >> n;
    vector<vector<pair<int,int>>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
      int a, b, w;
      cin >> a >> b >> w;
      adj[a].push_back({b, w});
      adj[b].push_back({a, w});
    }
    Lift lift = Lift(1, n, n, adj);
    while (true) {
      string s;
      cin >> s;
      if (s == "DONE") break;
      if (s == "DIST") {
        int a, b;
        cin >> a >> b;
        cout << lift.pathDistWeighted(a, b) << endl;
      } else {
        int a, b, k;
        cin >> a >> b >> k;
        cout << lift.kthOnPath(a, b, k-1) << endl;
      }
    }
  }
}