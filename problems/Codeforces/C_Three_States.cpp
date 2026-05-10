#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int INF = INT_MAX / 10;

const pair<int,int> dirs[4] = {{1,0},{-1,0},{0,1},{0,-1}};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    vector<string> grid(H); for (int i = 0; i < H; i++) cin >> grid[i];

    auto getDistMap = [&](char country) -> vector<vector<int>> {
        deque<tuple<int,int,int>> q; // holds (r, c, cost)
        for (int r = 0; r < H; r++) {
            for (int c = 0; c < W; c++) {
                if (grid[r][c] == country) {
                    q.push_back({r, c, 0});
                }
            }
        }
        vector<vector<int>> minD(H, vector<int>(W, INF));
        while (q.size()) {
            auto [r, c, cost] = q.front(); q.pop_front();
            if (minD[r][c] <= cost) continue;
            minD[r][c] = cost;
            for (auto [rd, cd] : dirs) {
                int nr = r + rd;
                int nc = c + cd;
                if (nr == H || nr < 0 || nc == W || nc < 0) continue;
                if (grid[nr][nc] == '#') continue;
                int ncost = cost;
                if (grid[nr][nc] == '.') ncost++;
                if (minD[nr][nc] <= ncost) continue;
                if (ncost == cost) {
                    q.push_front({nr, nc, ncost});
                } else {
                    q.push_back({nr, nc, ncost});
                }
            }
        }
        return minD;
    };

    auto mp1 = getDistMap('1');
    auto mp2 = getDistMap('2');
    auto mp3 = getDistMap('3');
    int out = INF;
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            int tot = mp1[r][c] + mp2[r][c] + mp3[r][c];
            if (grid[r][c] == '.') tot -= 2;
            out = min(out, tot);
        }
    }
    if (out >= INF) {
        cout << -1 << endl;
    } else {
        cout << out << endl;
    }
}