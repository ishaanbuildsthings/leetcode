#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int cities, roads, queries; cin >> cities >> roads >> queries;
    long long INF = (1LL << 60);
    vector<vector<long long>> dist(cities + 1, vector<long long>(cities + 1, INF));
    for (int i = 0; i < roads; i++) {
        int a, b; cin >> a >> b;
        long long c; cin >> c;
        dist[a][b] = min(dist[a][b], c);
        dist[b][a] = min(dist[b][a], c);
    }
    for (int node = 1; node <= cities; node++) {
        dist[node][node] = 0;
    }
    for (int middle = 1; middle <= cities; middle++) {
        for (int a = 1; a <= cities; a++) {
            for (int b = 1; b <= cities; b++) {
                long long withMiddle = dist[a][middle] + dist[b][middle];
                long long newDist = min(dist[a][b], withMiddle);
                dist[a][b] = newDist;
                dist[b][a] = newDist;
            }
        }
    }
    for (int i = 0; i < queries; i++) {
        int a, b; cin >> a >> b;
        long long minDist = dist[a][b];
        if (minDist == INF) {
            cout << -1 << endl;
        } else {
            cout << minDist << endl;
        }
    }
}