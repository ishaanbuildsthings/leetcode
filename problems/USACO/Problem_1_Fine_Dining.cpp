#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 4;

int main() {
    freopen("dining.in", "r", stdin);
    freopen("dining.out", "w", stdout);
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, k; cin >> n >> m >> k;
    vector<vector<pair<int,ll>>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b, w; cin >> a >> b >> w;
        adj[a].push_back({b, w});
        adj[b].push_back({a, w});
    }
    vector<pair<int,ll>> hay; // holds (index, yummy)
    for (int i = 0; i < k; i++) {
        int idx, yummy; cin >> idx >> yummy;
        hay.push_back({idx, yummy});
    }
    // first to a dijkstra from N to find the min distance from every node to N

    vector<ll> minFromN(n + 1, INF);

    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap; // holds (cost, node)
    heap.push({0, n});
    while (heap.size()) {
        auto [cost, node] = heap.top(); heap.pop();
        if (minFromN[node] <= cost) continue;
        minFromN[node] = cost;
        for (auto [adjN, adjW] : adj[node]) {
            ll ncost = cost + adjW;
            if (minFromN[adjN] <= ncost) continue;
            heap.push({ncost, adjN});
        }
    }

    // now we do a second dijkstra, every node with a hay bale has a starting cost of its distance - its hay bale
    priority_queue<pair<long long, int>, vector<pair<long long, int>>, greater<>> heap2; // holds (cost, node)
    for (auto [idx, yummy] : hay) {
        ll cost = minFromN[idx] - yummy;
        heap2.push({cost, idx});
    }
    vector<ll> minFromYummy(n + 1, INF);
    while (heap2.size()) {
        auto [cost, node] = heap2.top(); heap2.pop();
        if (minFromYummy[node] <= cost) continue;
        minFromYummy[node] = cost;
        for (auto [adjN, adjW] : adj[node]) {
            ll ncost = cost + adjW;
            if (minFromYummy[adjN] <= ncost) continue;
            heap2.push({ncost, adjN});
        }  
    }
    for (int node = 1; node < n; node++) {
        if (minFromYummy[node] <= minFromN[node]) {
            cout << 1 << '\n';
        } else {
            cout << 0 << '\n';
        }
    }
}