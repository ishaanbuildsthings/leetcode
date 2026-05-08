#include <bits/stdc++.h>
using namespace std;
using ll = long long;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m; cin >> n >> m;
  vector<vector<pair<int,int>>> adj(n + 1); // adj[node] -> [(adjNode, adjW), ...]
  for (int i = 0; i < m; i++) {
    int a, b, c; cin >> a >> b >> c;
    adj[a].push_back({b, c});
  }
  const ll INF = 1LL << 62;
  vector<long long> minDists(n + 1, INF); // minDists[node] is the minimum dist it takes to reach there
 
  using P = pair<ll, int>; // (dist, node)
  priority_queue<P, vector<P>, greater<P>> pq;
  pq.push({0, 1});
 
  while (!pq.empty()) {
    auto [dist, node] = pq.top(); pq.pop();
    if (minDists[node] <= dist) {
      continue;
    }
    minDists[node] = dist;
    for (auto [adjNode, adjW] : adj[node]) {
      if (minDists[adjNode] > adjW + dist) {
        pq.push({adjW + dist, adjNode});
      }
    }
  }
  for (int city = 1; city <= n; city++) {
    cout << minDists[city] << " ";
  }
}