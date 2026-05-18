#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const ll INF = LLONG_MAX / 4;
const ll MOD = 1000000007;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<pair<int,ll>>> adj(n + 1); // adj[node] -> [(adjN, adjW), ...]
    for (int i = 0; i < m; i++) {
        int a, b, c; cin >> a >> b >> c;
        adj[a].push_back({b, c});
    }
    vector<ll> minD(n + 1, INF);
    vector<ll> ways(n + 1, 0);
    vector<ll> minFlights(n + 1, INF);
    vector<ll> maxFlights(n + 1, -1 * INF);
    minFlights[1] = 0;
    maxFlights[1] = 0;
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap; // holds (cost, node)
    heap.push({0, 1});
    minD[1] = 0;
    ways[1] = 1;
    while (heap.size()) {
        auto [cost, node] = heap.top(); heap.pop();
        if (cost != minD[node]) continue;
        for (auto [adjN, adjW] : adj[node]) {
            ll ncost = cost + adjW;
            if (ncost < minD[adjN]) {
                ways[adjN] = ways[node];
                minD[adjN] = ncost;
                minFlights[adjN] = minFlights[node] + 1;
                maxFlights[adjN] = maxFlights[node] + 1;
                heap.push({ncost, adjN});
            } else if (ncost == minD[adjN]) {
                minFlights[adjN] = min(minFlights[adjN], minFlights[node] + 1);
                maxFlights[adjN] = max(maxFlights[adjN], maxFlights[node] + 1);
                ways[adjN] += ways[node];
                ways[adjN] %= MOD;
            }
        }
    }
    cout << minD[n] << " " << ways[n] << " " << minFlights[n] << " " << maxFlights[n];
}