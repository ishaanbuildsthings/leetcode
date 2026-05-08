#include <bits/stdc++.h>
using namespace std;
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n + 1); // adj[node] is a list of adjacent nodes
    vector<pair<int,int>> es(m);
    for (int i = 0; i < m; i++) {
      int a, b;
      cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }
    vector<bool> seen(n + 1, false);
 
    // count components
    function<void(int)> dfs = [&](int node) {
      seen[node] = true;
      for (auto adjNode : adj[node]) {
        if (seen[adjNode]) continue;
        dfs(adjNode);
      }
    };
 
    int res = 0; // new connections made
    int prev = -1;
    vector<pair<int,int>> newRoads;
    for (int node = 1; node <= n; node++) {
      if (seen[node]) continue;
      dfs(node);
      if (prev != -1) {
        res++;
        newRoads.push_back({prev, node});
      }
      prev = node;
    }
 
    cout << res << endl;
    for (auto [a, b] : newRoads) {
      cout << a << " " << b << endl;
    }
 
 
}