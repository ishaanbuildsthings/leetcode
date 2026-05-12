#include <bits/stdc++.h>
using namespace std;
using ll = long long;


int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int t; cin >> t;
  while (t--) {
    int n, m; cin >> n >> m;
    vector<vector<pair<int,ll>>> adj(n + 1);
    for (int i = 0; i < m; i++) {
      int a, b; cin >> a >> b;
      ll w; cin >> w;
      adj[a].push_back({b, w});
      adj[b].push_back({a, w});
    }
    using P = tuple<ll, int, int>; // holds (dist, slowness, node)
    priority_queue<P, vector<P>, greater<P>> pq;
    vector<int> slownessArr(n + 1);
    for (int i = 0; i < n; i++) cin >> slownessArr[i + 1];
    pq.push({0, slownessArr[1], 1});
    ll INF = 1LL << 62;
    vector<vector<ll>>minDist(n + 1, vector<ll>(1001, INF));// minDist[node][slownessAtNode]
    while (!pq.empty()) {
      auto [dist, slowness, node] = pq.top(); pq.pop();
      if (minDist[node][slowness] <= dist) continue;
      minDist[node][slowness] = dist;
      for (auto [adjN, adjW] : adj[node]) {
        int newSlow = min(slowness, slownessArr[adjN]);
        ll newDist = (adjW * slowness) + dist;
        if (minDist[adjN][newSlow] <= newDist) continue;
        pq.push({newDist, newSlow, adjN});
      }
    }
    ll res = INF;
    for (int slow = 1; slow <= 1000; slow++) {
      res = min(res, minDist[n][slow]);
    }
    cout << res << endl;
  }
}