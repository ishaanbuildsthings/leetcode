#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int INF = INT_MAX / 4;

pair<int,int> dirs[4] = {{1,0},{-1,0},{0,1},{0,-1}};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int H, W; cin >> H >> W;
    int sr, sc; cin >> sr >> sc; sr--; sc--;
    int lefts, rights; cin >> lefts >> rights;
    vector<string> grid(H);
    for (int i = 0; i < H; i++) {
        cin >> grid[i];
    }
    vector<vector<int>> minD(H, vector<int>(W, INF));
    deque<tuple<int,int,int>> q;
    q.push_back({sr, sc, 0}); // holds (r, c, cost)
    while (q.size()) {
        auto [r, c, cost] = q.front(); q.pop_front();
        if (minD[r][c] <= cost) continue;
        minD[r][c] = cost;
        for (auto [rd, cd] : dirs) {
            int nr = r + rd;
            int nc = c + cd;
            if (nr == H || nr < 0 || nc == W || nc < 0) continue;
            if (grid[nr][nc] == '*') continue;
            int ncost = cost;
            if (rd == 0 && cd == -1) {
                ncost++;
            }
            if (minD[nr][nc] <= ncost) continue;
            if (ncost == cost) {
                q.push_front({nr, nc, ncost});
            } else {
                q.push_back({nr, nc, ncost});
            }
        }
    }
    int out = 0;
    for (int r = 0; r < H; r++) {
        for (int c = 0; c < W; c++) {
            if (grid[r][c] == '*') continue;
            int leftsHere = minD[r][c];
            // leftsHere - rightsHere = left diff
            int leftDiff = sc - c;
            // -rightsHere = left diff - leftsHere
            // rightsHere = leftsHere - left diff
            int rightsHere = leftsHere - leftDiff;
            if (leftsHere <= lefts && rightsHere <= rights) {
                out++;
                // cerr << "r: " << r << " c: " << c << endl;
            }
        }
    }
    cout << out << endl;
}