#include <bits/stdc++.h>
using namespace std;
using ll = long long;

template <typename T>
void print1D(const vector<T>& v) {
    cout << "[";
    for (int i = 0; i < (int)v.size(); i++) {
        cout << v[i];
        if (i + 1 < (int)v.size()) cout << ", ";
    }
    cout << "]\n";
}

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, m, s, t; cin >> n >> m >> s >> t;
  vector<tuple<int,int,ll>> roads; // holds [(a, b, w), ...]
  vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
  vector<vector<pair<int,ll>>> inv(n + 1); // adj[node] -> [(adjN, adjW), ...]
  for (int i = 0; i < m; i++) {
    int a, b, w; cin >> a >> b >> w;
    adj[a].push_back({b, w});
    inv[b].push_back({a, w});
    roads.push_back({a, b, w});
  }
  ll INF = 1LL << 62;
  using vll = vector<ll>;
  using doubleRet = pair<vll,vll>;
  ll MOD = 167772161;
  function<doubleRet(int)> dijkstra = [&](int source) {
    vector<ll> res(n + 1, INF);
    vector<ll> ways(n + 1, 0);
    res[source] = 0;
    ways[source] = 1;
    using P = pair<ll,int>; // (dist, node)
    priority_queue<P, vector<P>, greater<P>> pq;
    pq.push({0, source});
    while (!pq.empty()) {
      auto [dist, node] = pq.top(); pq.pop();
      if (dist != res[node]) continue;
      // res[node] = dist;
      for (auto [adjN, adjW] : (source == s ? adj[node] : inv[node])) {
        if (adjW + dist < res[adjN]) {
          pq.push({adjW + dist, adjN});
          ways[adjN] = ways[node];
          res[adjN] = adjW + dist;
        } else if (adjW + dist == res[adjN]) {
          ways[adjN] += ways[node];
          ways[adjN] %= MOD;
        }
      }
    }
    return make_pair(res, ways);
  };

  // if our edge is part of the min, and it is part of all paths, print yes
  // if our edge is not part of the min, reduce to below the min if possible
  auto [from1, waysFrom1] = dijkstra(s);
  // print1D(from1);
  auto [fromn, waysFromN] = dijkstra(t);
  ll normalMin = from1[t];
  ll normalWays = waysFrom1[t];
  // cout << "normal min: " << normalMin << endl;
  // cout << "normal ways: " << normalWays << endl;
  for (auto [a, b, w] : roads) {
    // 1->a->b->n
    if (from1[a] == INF || fromn[b] == INF) {
      cout << "NO" << "\n";
      continue;
    }
    ll opt1 = from1[a] + w + fromn[b];
    // cout << "best dist with edge: " << opt1 << "\n";
    ll waysWithEdge = (waysFrom1[a] * waysFromN[b]) % MOD;
    // cout << "opt1 is: " << opt1 << endl;
    if (opt1 == normalMin && waysWithEdge == normalWays) {
      cout << "YES" << "\n";
    }
    else {
      if (opt1 - normalMin < w - 1) { // took 100 but normally can do in 95, edge weight is 8, it only needs to be 3
        cout << "CAN " << ((opt1 - normalMin) + 1) << "\n";
      } else {
        cout << "NO" << "\n";
      }
    }
  }
}