#include <bits/stdc++.h>
using namespace std;
using ll = long long;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m; cin >> n >> m;
  vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
  for (int i = 0; i < m; i++) {
    int a, b; cin >> a >> b;
    ll w; cin >> w;
    adj[a].push_back({b, w});
  }
  using P = tuple<ll,int,int>; // (distance, usedDiscount, node)
  priority_queue<P,vector<P>,greater<P>> pq;
  ll INF = 1LL << 62;
  vector<vector<ll>> minDist(n + 1, vector<ll>(2, INF)); // minDist[node][1] -> minDist
  pq.push({0, 0, 1});
  while (!pq.empty()) {
    auto [dist, usedDiscount, node] = pq.top(); pq.pop();
    if (minDist[node][usedDiscount] <= dist) continue;
    minDist[node][usedDiscount] = dist;
    for (auto [adjN, adjW] : adj[node]) {
      // no use
      if (adjW + dist < minDist[adjN][usedDiscount]) pq.push({adjW + dist, usedDiscount, adjN});
      // use
      if (!usedDiscount) {
        if (adjW / 2 + dist < minDist[adjN][1]) pq.push({adjW / 2 + dist, 1, adjN});
      }
    }
  }
  cout << minDist[n][1];
}