#include <bits/stdc++.h>
using namespace std;
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < m; i++) {
      int a, b;
      cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }
    bool impossible = false;
    vector<int> colors(n + 1, 2); // 2=uncolored
    function<void(int,int)> dfs = [&](int node, int color) {
      if (impossible) return;
      colors[node] = color;
      for (auto adjNode : adj[node]) {
        if (impossible) return;
        if (colors[adjNode] == colors[node]) {
          cout << "IMPOSSIBLE";
          impossible = true;
          return;
        }
        if (colors[adjNode] != 2) continue;
        dfs(adjNode, color ^ 1);
      }
    };
    for (int node = 1; node <= n; node++) {
      if (colors[node] == 2) {
        dfs(node, 1);
      }
    }
    if (impossible) return 0;
    for (int node = 1; node <= n; node++) {
      if (colors[node] == 2) {
        cout << 1 << " ";
      } else {
        cout << colors[node] + 1 << " ";
      }
    }
 
}