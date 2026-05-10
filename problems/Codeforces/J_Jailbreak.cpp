#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int INF = INT_MAX / 4;

const pair<int,int> dirs[4] = {{1,0},{-1,0},{0,1},{0,-1}};

void solve() {
    int H, W; cin >> H >> W;
    vector<string> grid(H + 2);
    for (int i = 0; i < H; i++) {
        string row; cin >> row;
        row = '.' + row + '.';
        grid[i + 1] = row;
    }
    grid[0] = string((W + 2), '.');
    grid[H + 1] = string((W + 2), '.');
    // . is empty
    // # is door
    // * is wall
    // $ is person

    auto getMinD = [&](vector<tuple<int,int,int>> sources) -> vector<vector<int>> {
        // sources is (r, c, cost)
        deque<tuple<int,int,int>> q;
        for (auto [r, c, cost] : sources) {
            if (cost == 0) {
                q.push_front({r, c, cost});
            } else {
                q.push_back({r, c, cost});
            }
        }
        vector<vector<int>> minD(H + 2, vector<int>(W + 2, INF));
        while (q.size()) {
            auto [r, c, cost] = q.front(); q.pop_front();
            if (minD[r][c] <= cost) continue;
            minD[r][c] = cost;
            for (auto [rd, cd] : dirs) {
                int nr = r + rd;
                int nc = c + cd;
                if (nr < 0 || nr == H + 2 || nc < 0 || nc == W + 2) continue;
                if (grid[nr][nc] == '*') continue;
                int ncost = cost;
                if (grid[nr][nc] == '#') ncost++;
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

    vector<tuple<int,int,int>> src1; // prisoner 1
    vector<tuple<int,int,int>> src2; // prisoner 2
    vector<tuple<int,int,int>> src3; // outside going in
    for (int r = 0; r < H + 2; r++) {
        for (int c = 0; c < W + 2; c++) {
            if (grid[r][c] == '$' && src1.size() == 0) {
                src1.push_back({r, c, 0});
            }
            else if (grid[r][c] == '$') {
                src2.push_back({r, c, 0});
            }
            if (r == 0 || r == H + 1 || c == 0 || c == W + 1) {
                src3.push_back({r, c, 0});
            }
        }
    }

    auto mp1 = getMinD(src1);
    auto mp2 = getMinD(src2);
    auto mp3 = getMinD(src3);

    int out = INF;
    for (int r = 0; r < H + 2; r++) {
        for (int c = 0; c < W + 2; c++) {
            int tot = mp1[r][c] + mp2[r][c] + mp3[r][c];
            if (grid[r][c] == '#') tot -= 2;
            out = min(out, tot); 
        }
    }
    cout << out << '\n';
    
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}