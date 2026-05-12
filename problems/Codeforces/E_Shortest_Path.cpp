#include <bits/stdc++.h>
using namespace std;
using ll = long long;

ll key(int a, int b, int c) {
  ll res = a;
  res |= (ll(b) << 12);
  res |= (ll(c) << 24);
  return res;
}

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m, k; cin >> n >> m >> k;
  vector<vector<int>> adj(n + 1);
  for (int i = 0; i < m; i++) {
    int a, b; cin >> a >> b;
    adj[a].push_back(b);
    adj[b].push_back(a);
  }
  unordered_set<ll> bad;
  for (int i = 0; i < k; i++) {
    int a, b, c; cin >> a >> b >> c;
    bad.insert(key(a, b, c));
  }
  ll INF = 1LL << 62;
  using P = tuple<ll,int,int>; // holds (dist, node, prevNode)
  vector<vector<int>> parents(n + 1, vector<int>(n + 1, 0)); // parents[node][prevNode] = the node BEFORE arriving at this state lol
  priority_queue<P, vector<P>, greater<P>> pq; // holds (dist, node, prevNode)
  vector<vector<ll>> minDists(n + 1, vector<ll>(n + 1, INF)); // minDists[node][prevNode] = smallest distance to arrive at this state
  minDists[1][0] = 0;
  // for (int node = 1; node <= n; node++) {
  //   minDists[1][node] = 0;
  // }
  pq.push({0, 1, 0});
  while (!pq.empty()) {
    auto [dist, node, prevNode] = pq.top(); pq.pop();
    if (minDists[node][prevNode] != dist) continue;
    for (auto adjN : adj[node]) {
      if (bad.count(key(prevNode, node, adjN))) continue;
      ll nd = dist + 1;
      if (nd < minDists[adjN][node]) {
        minDists[adjN][node] = nd;
        pq.push({nd, adjN, node});
        parents[adjN][node] = prevNode;
      }
    }
  }
  ll minResult = INF;
  int resPrev = 0;
  for (int prevNode = 0; prevNode <= n; prevNode++) {
    if (minDists[n][prevNode] < minResult) {
      minResult = minDists[n][prevNode];
      resPrev = prevNode;
    }
  }
  if (minResult == INF) {
    cout << -1;
    return 0;
  }
  cout << minResult << endl;
  // cout << "min result: " << minResult << " res prev: " << resPrev << endl;
  vector<int> path;
  int curr = n;
  int prev = resPrev;
  while (curr != 1) {
    path.push_back(curr);
    int newPP = parents[curr][prev];
    curr = prev;
    prev = newPP;
  }
  path.push_back(1);
  for (int i = path.size() - 1; i >= 0; i--) {
    cout << path[i] << " ";
  }
}