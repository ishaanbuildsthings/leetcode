#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const ll INF = LLONG_MAX / 4;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k; cin >> n >> m >> k;
    vector<vector<pair<int,ll>>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        ll w; cin >> w;
        adj[a].push_back({b, w});
    }
    // minD[node] -> top K cheapest paths
    vector<vector<ll>> minD(n + 1, vector<ll>(k, INF));
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap; // holds (cost, node)
    heap.push({0, 1});
    while (heap.size()) {
        auto [cost, node] = heap.top(); heap.pop();
        auto& bucket = minD[node];
        if (bucket[bucket.size() - 1] <= cost) continue;
        bucket.push_back(cost);
        sort(bucket.begin(), bucket.end());
        bucket.pop_back();
        for (auto [adjNode, adjW] : adj[node]) {
            ll ncost = cost + adjW;
            heap.push({ncost, adjNode});
        }
    }
    auto& bucket = minD[n];
    for (auto x : bucket) cout << x << " ";
}