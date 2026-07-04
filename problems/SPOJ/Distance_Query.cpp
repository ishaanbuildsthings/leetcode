#include <bits/stdc++.h>
using namespace std;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n;
  cin >> n;
  vector<vector<pair<int,int>>> adj(n + 1);
  for (int i = 0; i < n - 1; i++) {
    int a, b, w;
    cin >> a >> b >> w;
    adj[a].push_back({b, w});
    adj[b].push_back({a, w});
  }
  int INF = 100000000;
  int LOG = 32 - __builtin_clz(n);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
  vector<vector<int>> mx(LOG, vector<int>(n + 1));
  vector<vector<int>> mn(LOG, vector<int>(n + 1));
  vector<int> depths(n + 1);
  function<void(int,int,int)> dfs = [&](int node, int parent, int wToP) {
    up[0][node] = parent;
    depths[node] = node == 0 ? 0 : depths[parent] + 1;
    mx[0][node] = node == 0 ? 0 : wToP;
    mn[0][node] = node == 0 ? INF : wToP;
    for (int k = 1; k < LOG; k++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
      mx[k][node] = max(mx[k-1][node], mx[k-1][mid]);
      mn[k][node] = min(mn[k-1][node], mn[k-1][mid]);
    }
    for (auto [adjN, adjW] : adj[node]) {
      if (adjN != parent) {
        dfs(adjN, node, adjW);
      }
    }
  };
  dfs(1, 1, 0);
  int k;
  cin >> k;
  for (int i = 0; i < k; i++) {
    int a, b;
    cin >> a >> b;
    if (depths[a] < depths[b]) swap(a, b);
    int shortest = INF;
    int longest = 0;
    int diff = depths[a] - depths[b];
    for (int power = 0; power < LOG; power++) {
      if (diff >> power & 1) {
        shortest = min(shortest, mn[power][a]);
        longest = max(longest, mx[power][a]);
        a = up[power][a];
      }
    }
    if (a == b) {
      cout << shortest << " " << longest << endl;
      continue;
    }
    for (int power = LOG - 1; power >= 0; power--) {
      if (up[power][a] != up[power][b]) {
        shortest = min(shortest, mn[power][a]);
        longest = max(longest, mx[power][a]);
        shortest = min(shortest, mn[power][b]);
        longest = max(longest, mx[power][b]);
        a = up[power][a];
        b = up[power][b];
      }
    }
    shortest = min(shortest, mn[0][a]);
    longest = max(longest, mx[0][a]);
    shortest = min(shortest, mn[0][b]);
    longest = max(longest, mx[0][b]);
    cout << shortest << " " << longest << endl;
  }
}