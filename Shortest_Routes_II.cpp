#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll INF = LLONG_MAX / 4;

const int MAX_N = 500;
// ll cache[MAX_N + 1][MAX_N + 1][MAX_N + 1]; // FOR TOP DOWN (MLE)

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q; cin >> n >> m >> q;


    // ====================================
    // HEAPLESS DIJKSTRA
    vector<vector<pair<int,ll>>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b, c; cin >> a >> b >> c;
        adj[a].push_back({b, c});
        adj[b].push_back({a, c});
    }

    auto dijkstra = [&](int source) -> vector<ll> {
        vector<ll> minD(n + 1, INF);
        vector<int> visited(n + 1, 0);
        minD[source] = 0;
        for (int op = 0; op < n; op++) {
            // find cheapest unvisited node
            ll cheapest = INF;
            int bestNode = -1;
            for (int node = 1; node <= n; node++) {
                if (visited[node]) continue;
                if (minD[node] < cheapest) {
                    cheapest = minD[node];
                    bestNode = node;
                }
            }
            if (bestNode == -1) break;
            visited[bestNode] = 1;
            for (auto [adjN, adjW] : adj[bestNode]) {
                ll nweight = cheapest + adjW;
                nweight = min(nweight, INF);
                minD[adjN] = min(minD[adjN], nweight);
            }
        }
        return minD;
    };

    vector<vector<ll>> dijkstras(n + 1);
    for (int node = 1; node <= n; node++) {
        dijkstras[node] = dijkstra(node);
    }

    for (int i = 0; i < q; i++) {
        int a, b; cin >> a >> b;
        ll ans = dijkstras[a][b];
        if (ans == INF) {
            cout << -1 << '\n';
        } else {
            cout << ans << '\n';
        }
    }


    



    // ====================================
    // BOTTOM UP FLOYD WARSHALL
    // vector<vector<ll>> dp(n + 1, vector<ll>(n + 1, INF));
    // for (int i = 0; i < m; i++) {
    //     int a, b, c; cin >> a >> b >> c;
    //     dp[a][b] = min(dp[a][b], 1LL * c);
    //     dp[b][a] = min(dp[b][a], 1LL * c);
    // }
    // for (int i = 1; i <= n; i++) dp[i][i] = 0;

    // for (int middle = 1; middle <= n; middle++) {
    //     for (int node1 = 1; node1 <= n; node1++) {
    //         for (int node2 = 1; node2 <= n; node2++) {
    //             dp[node1][node2] = min(dp[node1][node2], dp[node1][middle] + dp[middle][node2]);
    //         }
    //     }
    // }

    // for (int i = 0; i < q; i++) {
    //     int a, b; cin >> a >> b;
    //     ll ans = dp[a][b];
    //     if (ans == INF) {
    //         cout << -1 << '\n';
    //     } else {
    //         cout << ans << '\n';
    //     }
    // }

    // ====================================

    
    // TOP DOWN (too much memory)
    // for (int i = 0; i <= MAX_N; i++) {
    //     for (int j = 0; j <= MAX_N; j++) {
    //         for (int k = 0; k <= MAX_N; k++) {
    //             cache[i][j][k] = -1;
    //         }
    //     }
    // }

    // auto dp = [&](auto&& self, int node1, int node2, int middle) -> ll {
    //     if (middle == 0) {
    //         ll minD = minDist[node1][node2];
    //         return minD;
    //     }
    //     auto& res = cache[node1][node2][middle];
    //     if (res != -1) return res;

    //     ll ifTake = self(self, node1, middle, middle - 1) + self(self, middle, node2, middle - 1);
    //     if (ifTake > INF) {
    //         ifTake = INF;
    //     }
    //     ll ifSkip = self(self, node1, node2, middle - 1);
    //     res = min(ifTake, ifSkip);
    //     return res;
    // };

    // for (int i = 0; i < q; i++) {
    //     int a, b; cin >> a >> b;
    //     ll ans = dp(dp, a, b, n);
    //     if (ans == INF) {
    //         cout << -1 << '\n';
    //     } else {
    //         cout << ans << '\n';
    //     }
    // }
}