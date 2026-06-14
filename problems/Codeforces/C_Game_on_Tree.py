#include <bits/stdc++.h>
using namespace std;

int n;
vector<vector<int>> adj; // adj[n1] is a list of adj nodes
vector<int> numParents; // numParents[node] is the # of parents

void dfs(int node, int par, int parentCount) {
  numParents[node] = parentCount;
  for (int adjNode : adj[node]){
    if (adjNode != par) {
      dfs(adjNode, node, parentCount + 1);
    }
  }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    cin >> n;
    adj.resize(n + 1);
    numParents.resize(n + 1);

    for (int i = 0; i < n - 1; i++) {
      int a, b;
      cin >> a >> b;
      adj[a].push_back(b);
      adj[b].push_back(a);
    }
    dfs(1, -1, 0);

    double res = 0.0;
    for (int node = 1; node <= n; node++) {
      double probability = 1.0 / (numParents[node] + 1);
      res += probability;
    }
    cout << fixed << setprecision(15) << res << endl;
}