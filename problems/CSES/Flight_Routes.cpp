#include <bits/stdc++.h>
using namespace std;
using ll = long long;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m, k; cin >> n >> m >> k;
  vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
  for (int i = 0; i < m; i++) {
    int a, b; cin >> a >> b;
    ll w; cin >> w;
    adj[a].push_back({b, w});
  }
  // minDist[node] is the k smallest
  vector<vector<ll>> minDist(n + 1); // minDist[node] -> [1, 2, 3]
  using P = pair<ll, int>; // (dist, node)
  priority_queue<P, vector<P>, greater<P>> pq;
  pq.push({0, 1}); // (dist, node)
  while (!pq.empty()) {
    auto [dist, node] = pq.top(); pq.pop();
    if (int(minDist[node].size()) == k) continue;
    minDist[node].push_back(dist);
    // minDist[node].push_back(dist);
    // if (minDist[node].size() == k) {
    //   ll mx = dist;
    //   for (auto v : minDist[node]) {
    //     mx = max(mx, v);
    //   }
    //   auto it = find(minDist[node].begin(), minDist[node].end(), mx);
    // }
    // minDist[node].erase(it);
    for (auto [adjN, adjW] : adj[node]) {
      ll nDist = dist + adjW;
      if (minDist[adjN].size() < k) {
        pq.push({nDist, adjN});
      }
    }
  }
  for (auto v : minDist[n]) {
    cout << v << " ";
  }
}