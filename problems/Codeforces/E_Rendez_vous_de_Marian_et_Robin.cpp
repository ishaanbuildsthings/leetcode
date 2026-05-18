#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int TESTS; cin >> TESTS;
  while (TESTS--) {
    // cout << "test: " << endl;


    int n, m, h; cin >> n >> m >> h;
    vector<bool> horse(n + 1);
    for (int i = 0; i < h; i++) {
      int has; cin >> has;
      horse[has] = true;
    }
    vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
    for (int i = 0; i < m; i++) {
      int a, b, w; cin >> a >> b >> w;
      adj[a].push_back({b, w});
      adj[b].push_back({a, w});
    }
    ll INF = 1LL << 60;
    vector<vector<ll>> minFrom1(n + 1, vector<ll>(2, INF)); // minFrom1[arriveNode][withHorse] -> min dist to reach this state
    minFrom1[1][0] = 0;
    using P = tuple<ll,int,int>; // (dist, hasHorse, node)
    priority_queue<P, vector<P>, greater<P>> pq;
    pq.push({0, 0, 1});
    while (!pq.empty()) {
      auto [dist, hasHorse, node] = pq.top(); pq.pop();
      if (minFrom1[node][hasHorse] != dist) continue;
      int newHorse = hasHorse == 1 ? 1 : horse[node] ? 1 : 0;
      for (auto [adjN, adjW] : adj[node]) {
        ll newDist = dist + (newHorse ? (adjW / 2) : adjW);
        if (newDist < minFrom1[adjN][newHorse]) {
          minFrom1[adjN][newHorse] = newDist;
          pq.push({newDist, newHorse, adjN});
        }
      }
    }


    vector<vector<ll>> minFromN(n + 1, vector<ll>(2, INF));
    minFromN[n][0] = 0;
    priority_queue<P, vector<P>, greater<P>> pq2;
    pq2.push({0, 0, n});
    while (!pq2.empty()) {
      auto [dist, hasHorse, node] = pq2.top(); pq2.pop();
      if (minFromN[node][hasHorse] != dist) continue;
      int newHorse = hasHorse == 1 ? 1 : horse[node] ? 1 : 0;
      for (auto [adjN, adjW] : adj[node]) {
        ll newDist = dist + (newHorse ? (adjW / 2) : adjW);
        if (newDist < minFromN[adjN][newHorse]) {
          minFromN[adjN][newHorse] = newDist;
          pq2.push({newDist, newHorse, adjN});
        }
      }
    }

    ll res = INF;
    for (int node = 1; node <= n; node++) {
      ll arrive1 = min(minFrom1[node][1], minFrom1[node][0]);
      ll arrive2 = min(minFromN[node][1], minFromN[node][0]);
      res = min(res, max(arrive1, arrive2));
      // res = min(res, max((min(minFrom1[node][1], minFrom1[node][0]), min(minFromN[node][1], minFromN[node][0]))));
    }
    // cout << "res is: " << res << endl;
    if (res == INF) cout << -1 << endl;
    else cout << res << "\n";


  }
}