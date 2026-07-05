#include <bits/stdc++.h>
using namespace std;

constexpr size_t MAX_SHADES = 251;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int t;
  cin >> t;
  while (t--) {
    int n, q, r;
    cin >> n >> q >> r;
    vector<int> shades(n);
    for (int i = 0; i < n; i++) cin >> shades[i];

    vector<bitset<MAX_SHADES>> subtreeBitsets(n);

    vector<vector<int>> adj(n);
    for (int i = 0; i < n - 1; i++) {
      int a, b; cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }

    int LOG = 32 - __builtin_clz(n);

    vector<vector<int>> up(LOG, vector<int>(n));
    vector<vector<bitset<MAX_SHADES>>> upShades(LOG, vector<bitset<MAX_SHADES>>(n));
    vector<int> depths(n);

    // fill out subtree bitsets
    function<void(int,int)> fillBs = [&](int node, int parent) {
      subtreeBitsets[node].set(shades[node]);
      for (auto child : adj[node]) {
        if (child != parent) {
          fillBs(child, node);
          subtreeBitsets[node] |= subtreeBitsets[child];
        }
      }
    };
    fillBs(r, r);

    function<void(int,int)> dfs = [&](int node, int parent) {
      depths[node] = node == r ? 0 : depths[parent] + 1;
      up[0][node] = parent;
      upShades[0][node] = subtreeBitsets[node];
      subtreeBitsets[node].set(shades[node]);
      for (int k = 1; k < LOG; k++) {
        int mid = up[k-1][node];
        up[k][node] = up[k-1][mid];
        bitset<MAX_SHADES> shadeToMid = upShades[k-1][node];
        upShades[k][node] = shadeToMid | upShades[k-1][mid];
      }
      for (auto child : adj[node]) {
        if (child == parent) continue;
        dfs(child, node);
      }

    };
    dfs(r, r);

    function<long long(int,int)> unique = [&](int a, int b) {
      // int initA = a;
      // int initB = b;
      if (depths[a] < depths[b]) swap(a, b); // a goes deeper
      bitset<MAX_SHADES> merged;
      int diff = depths[a] - depths[b];
      for (int k = 0; k < LOG; k++) {
        if (diff >> k & 1) {
          merged |= upShades[k][a];
          a = up[k][a];
        }
      }
      if (a == b) {
        merged |= upShades[0][a];
        return merged.count();
      }
      for (int k = LOG - 1; k >= 0; k--) {
        if (up[k][a] != up[k][b]) {
          merged |= upShades[k][a];
          merged |= upShades[k][b];
          a = up[k][a];
          b = up[k][b];
        }
      }
      merged |= upShades[0][a];
      merged |= upShades[0][b];
      int lca = up[0][a];
      merged |= upShades[0][lca];
      return merged.count();
    };

    for (int i = 0; i < q; i++) {
      int a, b; cin >> a >> b; // query path
      cout << unique(a, b) << '\n';
    }
  }
}