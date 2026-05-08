#include <bits/stdc++.h>
using namespace std;
using ll = long long;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m; cin >> n >> m;
  int MOD = 1000000000 + 7;
  vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
  for (int i = 0; i < m; i++) {
    int a, b, c; cin >> a >> b >> c;
    adj[a].push_back({b, c});
  }
 
  ll INF = 1LL << 62;
 
  // Dijkstra #1, compute min price + ways to arrive in price
  vector<ll> minDist(n + 1, INF);
  vector<ll> ways(n + 1, 0);
  minDist[1] = 0;
  ways[1] = 1;
  using P = pair<ll, int>; // holds (dist, node)
  priority_queue<P, vector<P>, greater<P>> pq;
  pq.push({0, 1});
  while (!pq.empty()) {
    auto [dist, node] = pq.top(); pq.pop();
    if (minDist[node] != dist) continue;
    for (auto [adjN, adjW] : adj[node]) {
      ll nd = adjW + dist;
      if (nd < minDist[adjN]) {
        minDist[adjN] = nd;
        ways[adjN] = ways[node];
        pq.push({nd, adjN});
      } else if (nd == minDist[adjN]) {
        ways[adjN] += ways[node];
        ways[adjN] %= MOD;
      }
    }
  }
  cout << minDist[n] << " ";
  cout << ways[n] << " ";
 
  // Dijkstra #2, compute min price + min flights
  vector<pair<ll,int>> minDistAndFlights(n + 1, make_pair(INF, -1)); // minDistAndFlights[node] -> (smallest dist, smallest flights for that dist)
  minDistAndFlights[1] = make_pair(0, 0);
  using P2 = tuple<ll, int, int>; // holds (dist, flights, node)
  priority_queue<P2, vector<P2>, greater<P2>> pq2;
  pq2.push({0, 0, 1});
  while (!pq2.empty()) {
    auto [dist, minFlights, node] = pq2.top(); pq2.pop();
    if (make_pair(dist, minFlights) != minDistAndFlights[node]) continue;
    for (auto [adjN, adjW] : adj[node]) {
      ll nd = adjW + dist;
      if (make_pair(nd, minFlights + 1) < minDistAndFlights[adjN]) {
        minDistAndFlights[adjN] = make_pair(nd, minFlights + 1);
        pq2.push({nd, minFlights + 1, adjN});
      }
    }
  }
  cout << minDistAndFlights[n].second << " ";
 
  // Dijkstra #3, compute min price + max flights
  vector<pair<ll,int>> maxDistAndFlights(n + 1, make_pair(INF, -1)); // maxDistAndFlights[node] -> (smallest dist, max flights for that dist)
  maxDistAndFlights[1] = make_pair(0, 0);
  using P3 = tuple<ll, int, int>; // holds (dist, flights, node)
  priority_queue<P3, vector<P3>, greater<P3>> pq3;
  pq3.push({0, 0, 1});
  while (!pq3.empty()) {
    auto [dist, maxFlights, node] = pq3.top(); pq3.pop();
    if (make_pair(dist, maxFlights) != maxDistAndFlights[node]) continue;
    for (auto [adjN, adjW] : adj[node]) {
      ll nd = adjW + dist;
      // maxFlights - 1 because I use negatives
      if (make_pair(nd, maxFlights - 1) < maxDistAndFlights[adjN]) {
        maxDistAndFlights[adjN] = make_pair(nd, maxFlights - 1);
        pq3.push({nd, maxFlights - 1, adjN});
      }
    }
  }
  cout << -1 * maxDistAndFlights[n].second << " ";
}