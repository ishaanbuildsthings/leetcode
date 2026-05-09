#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const pair<int,int> DIFFS[] = {{-1,0}, {1,0}, {0,-1}, {0,1}};
const int INF = INT_MAX / 4;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    int startR, startC; cin >> startR >> startC; startR--; startC--;
    int endR, endC; cin >> endR >> endC; endR--; endC--;
    vector<string> grid(H); for (int i = 0; i < H; i++) cin >> grid[i];

    deque<tuple<int,int,int>> q; // holds (r, c, cost)
    q.push_back({startR, startC, 0});
    vector<vector<int>> minD(H, vector<int>(W, INF));

    while (q.size()) {
        auto [r, c, cost] = q.front(); q.pop_front();
        if (cost >= minD[r][c]) continue;
        minD[r][c] = cost;
        for (auto& [rd, cd] : DIFFS) {
            int nr = r + rd;
            int nc = c + cd;
            if (nr < 0 || nr == H || nc < 0 || nc == W) continue;
            if (grid[nr][nc] == '#') continue;
            if (cost >= minD[nr][nc]) continue;
            q.push_front({nr, nc, cost});
        }
        for (int rdiff = -2; rdiff <= 2; rdiff++) {
            for (int cdiff = -2; cdiff <= 2; cdiff++) {
                if (rdiff == 0 && cdiff == 0) continue;
                int nr = r + rdiff;
                int nc = c + cdiff;
                if (nr < 0 || nr >= H || nc < 0 || nc >= W) continue;
                if (grid[nr][nc] == '#') continue;
                if (cost + 1 >= minD[nr][nc]) continue;
                q.push_back({nr, nc, cost + 1});
            }
        }
    } 
    if (minD[endR][endC] == INF) {
        cout << -1 << endl;
    } else {
        cout << minD[endR][endC] << endl;
    }

}