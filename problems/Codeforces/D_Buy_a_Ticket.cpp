#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 2;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<pair<int,ll>>> adj(n); // adj[node] -> (adjN, w)
    for (int i = 0; i < m; i++) {
        int a, b;
        ll w;
        cin >> a >> b; a--; b--;
        cin >> w;
        adj[a].push_back({b, w});
        adj[b].push_back({a, w});
    }

    vector<ll> prices(n); for (int i = 0; i < n; i++) cin >> prices[i];

    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap; // holds (cost, node)
    for (int i = 0; i < n; i++) {
        ll price = prices[i];
        heap.push({price, i});
    }
    
    vector<ll> minD(n, INF);
    while (heap.size()) {
        auto [cost, node] = heap.top(); heap.pop();
        if (minD[node] <= cost) continue;
        minD[node] = cost;
        for (auto [adjN, w] : adj[node]) {
            ll ncost = cost + 2LL * w;
            if (minD[adjN] <= ncost) continue;
            heap.push({ncost, adjN});
        }
    }
    for (auto x : minD) {
        cout << x << " ";
    }
}