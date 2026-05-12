#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int TESTS; cin >> TESTS;
  while (TESTS--) {
    // cout << "test: " << endl;
    int n, m; cin >> n >> m;
    string symptomsString; cin >> symptomsString;
    int symptoms = stoi(symptomsString, nullptr, 2);
    // cout << "SYMPTOMS: " << symptoms << endl;
    vector<tuple<int,int,int>> meds; // holds (days, healMask, painMask)
    for (int i = 0; i < m; i++) {
      int days; cin >> days;
      string healString; cin >> healString;
      string painString; cin >> painString;
      int heal = stoi(healString, nullptr, 2);
      int pain = stoi(painString, nullptr, 2);
      meds.push_back({days, heal, pain});
    }
    using P = pair<ll,int>; // (dist, node)
    priority_queue<P, vector<P>, greater<P>> pq;
    pq.push({0, symptoms});
    ll INF = 1LL << 62;
    vector<ll> minDist((1 << n) + 1, INF);
    while (!pq.empty()) {
      auto [dist, node] = pq.top(); pq.pop();
      if (minDist[node] <= dist) continue;
      minDist[node] = dist;
      for (auto [days, healMask, painMask] : meds) {
        ll nDist = days + dist;
        // clear out healed
        int postHeal = node & ~healMask;
        postHeal |= painMask;
        if (minDist[postHeal] <= nDist) continue;
        pq.push({nDist, postHeal});
      }
    }
    // cout << "ans: " << endl;
    cout << ((minDist[0] == INF) ? -1 : minDist[0]) << endl;
  }
}