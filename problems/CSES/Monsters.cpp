#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int INF = INT_MAX;
const pair<int,int> dirs[4] = {{1,0},{-1,0},{0,1},{0,-1}};
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    vector<string> grid(H);
    for (int i = 0; i < H; i++) cin >> grid[i];

    auto minD = [&](vector<pair<int,int>>& srcs) -> pair<vector<vector<int>>, vector<vector<pair<int,int>>>> {
        deque<pair<int,int>> q;
        for (auto [r, c] : srcs) {
            q.push_back({r, c});
        }
        vector<vector<pair<int,int>>> parent(H, vector<pair<int,int>>(W, {-1, -1}));
        vector<vector<int>> minDists(H, vector<int>(W, INF));
        int steps = 0;
        while (q.size()) {
            int length = q.size();
            for (int i = 0; i < length; i++) {
                auto [r, c] = q.front(); q.pop_front();
                minDists[r][c] = steps;
                for (auto [rd, cd] : dirs) {
                    int nr = r + rd;
                    int nc = c + cd;
                    if (nr < 0 || nr == H || nc < 0 || nc == W) continue;
                    if (grid[nr][nc] == '#') continue;
                    if (minDists[nr][nc] <= steps + 1) continue;
                    minDists[nr][nc] = steps + 1;
                    parent[nr][nc] = {r, c};
                    q.push_back({nr, nc});
                }
            }
            steps++;
        }
        return {minDists, parent};
    };

    vector<pair<int,int>> monsters;
    vector<pair<int,int>> hero;
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            if (grid[r][c] == 'M') {
                monsters.push_back({r, c});
            }
            if (grid[r][c] == 'A') {
                hero.push_back({r, c});
            }
        }
    }
    if (hero[0].first == 0 || hero[0].first == H - 1 || hero[0].second == 0 || hero[0].second == W - 1) {
        cout << "YES" << endl;
        cout << 0 << endl;
        return 0;
    }
    auto [mMinDist, mParent] = minD(monsters);
    auto [hMinDist, hParent] = minD(hero);
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            if (grid[r][c] == '.' && (r == 0 || r == H - 1 || c == 0 || c == W - 1)) {
                if (hMinDist[r][c] < mMinDist[r][c]) {
                    cout << "YES" << endl;
                    cout << hMinDist[r][c] << endl;
                    // cout << "found r=" << r << " c=" << c << endl;
                    vector<pair<int,int>> path;
                    int currR = r;
                    int currC = c;
                    path.push_back({currR, currC});
                    while (hParent[currR][currC].first != -1){ 
                        int newR = hParent[currR][currC].first;
                        int newC = hParent[currR][currC].second;
                        currR = newR;
                        currC = newC;
                        path.push_back({currR, currC});
                    }
                    // for (auto [rp, cp] : path) {
                    //     cout << rp << "," << cp << " ";
                    // }
                    reverse(path.begin(), path.end());
                    for (int i = 0; i < path.size() - 1; i++) {
                        auto [r1, c1] = path[i];
                        auto [r2, c2] = path[i + 1];
                        if (r2 == r1 + 1) {
                            cout << "D";
                        } else if (r2 == r1 - 1) {
                            cout << "U";
                        } else if (c2 == c1 + 1) {
                            cout << "R";
                        } else {
                            cout << "L";
                        }
                    }
                    return 0;
                }
            }
        }
    }

    cout << "NO";
}