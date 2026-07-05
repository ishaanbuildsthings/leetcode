#include <iostream>

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
    int n, q;
    cin >> n >> q;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < n - 1; i++) {
      int a, b; cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }
    vector<int> sz(n + 1);
    vector<int> depths(n + 1);
    function<void(int, int)> dfs = [&](int node, int parent) {
      sz[node] = 1;
      depths[node] = node == 1 ? 0 : depths[parent] + 1;
      for (auto child : adj[node]) {
        if (child == parent) continue;
        dfs(child, node);
        sz[node] += sz[child];
      }
    };
    dfs(1, -1);

    Lift lift = Lift(1, n, n, adj);
    while (q--) {
      // cout << "-----------" << endl;
      int a, b, c; cin >> a >> b >> c;
      if (!lift.inPath(a, b, c)) {
        cout << 0 << endl;
        continue;
      }
      int res = 0;
      // if we are the LCA, we score our parent-outside-subtree score
      int ab = lift.lca(a, b);
      if (ab == c) {
        res += (n - sz[ab]);
        // cout << "we are the lca so we score parent" << endl;
      }
      res += sz[c]; // we should score the entire subtree
      // but we need to lose any children thats on the path a<>b
      // cout << "we score entire subtree now we are: " << res << endl;
      int toA = lift.kthOnPath(c, a, 2);
      if (lift.inPath(a, b, toA) && depths[toA] > depths[c]) {
        res -= sz[toA];
      }
      int toB = lift.kthOnPath(c, b, 2);
      if (lift.inPath(a, b, toB) && depths[toB] > depths[c]) {
        res -= sz[toB];
      }
      cout << res << endl;
    }
}