#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m, q; cin >> n >> m >> q;
    vector<vector<int>> adj(n + 1);
    for (int i = 0; i < m; i++) {
        int a, b; cin >> a >> b;
        adj[a].push_back(b);
        adj[b].push_back(a);
    }
    struct Query {
        int a, b, x;
    };
    vector<Query> queries;
    for (int i = 0; i < q; i++) {
        int a, b, x; cin >> a >> b >> x;
        queries.push_back({a, b, x});
    }
    const ll INF = LLONG_MAX / 4;
    // minDistEven[startNode][endNode] = minDist to go from start->end in even moves
    vector<vector<ll>> minDistEven(n + 1, vector<ll>(n + 1, INF));
    
    // minDistOdd[startNode][endNode] = minDist to go from start->end in even moves
    vector<vector<ll>> minDistOdd(n + 1, vector<ll>(n + 1, INF));
    
    for (int startNode = 1; startNode <= n; startNode++) {
        queue<pair<int,int>> queue; // holds (node, parity)
        queue.push({startNode, 0});
        vector<ll> minD_Even(n + 1, INF);
        minD_Even[startNode] = 0;
        vector<ll> minD_Odd(n + 1, INF);
        int steps = 0;
        while (queue.size()) {
            int length = queue.size();
            for (int i = 0; i < length; i++) {
                auto [node, parity] = queue.front(); queue.pop();
                for (auto adjN : adj[node]) {
                    int np = parity ^ 1;
                    ll old = (np == 1 ? minD_Odd[adjN] : minD_Even[adjN]);
                    if (old == INF) {
                        if (np == 1) {
                            minD_Odd[adjN] = steps + 1;
                        } else {
                            minD_Even[adjN] = steps + 1;
                        }
                        queue.push({adjN, np});
                    }
                }
            }   
            steps++;
        }
        minDistEven[startNode] = minD_Even;
        minDistOdd[startNode] = minD_Odd;
    }
    for (auto [a, b, x] : queries) {
        ll minimum = (x % 2 == 1 ? minDistOdd[a][b] : minDistEven[a][b]);
        if (minimum <= x) {
            cout << "YES" << '\n';
        } else {
            cout << "NO" << '\n';
        }
    }
    
    
}