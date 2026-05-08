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
 
    queue<int> q;
    q.push(1);
    vector<bool> seen(n + 1, false);
    vector<int> parents(n + 1, -1); // parent[node] is the previous node in the bfs
 
    seen[1] = true;
    while (!q.empty()) {
      int length = q.size();
      for (int i = 0; i < length; i++) {
        int popped = q.front();
        q.pop();
        for (auto adjNode : adj[popped]) {
          if (seen[adjNode]) continue;
          seen[adjNode] = true;
          parents[adjNode] = popped;
          q.push(adjNode);
        }
      }
    }
 
    if (parents[n] == -1) {
      cout << "IMPOSSIBLE";
      return 0;
    }
 
    vector<int> res;
    for (int curr = n; curr != -1; curr = parents[curr]) {
      res.push_back(curr);
    }
    reverse(res.begin(), res.end());
 
    cout << res.size() << endl;
    for (auto v : res) {
      cout << v << " ";
    }
 
 
 
 
 
}