#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int INF = INT_MAX / 2;

const pair<int,int> dirs[4] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    int H, W, k; cin >> H >> W >> k;
    vector<string> grid(H);
    for (int i = 0; i < H; i++) {
        cin >> grid[i];
    }
    int x1, y1, x2, y2; cin >> x1 >> y1 >> x2 >> y2; x1--; y1--; x2--; y2--;

    vector<vector<int>> minD(H, vector<int>(W, INF));
    minD[x1][y1] = 0;
    int steps = 0;
    deque<pair<int,int>> q; // holds (r, c)
    q.push_back({x1, y1});
    set<pair<int,int>> seen;
    seen.insert({x1, y1});
    while (q.size()) {
        int length = q.size();
        for (int i = 0; i < length; i++) {
            auto [r, c] = q.front(); q.pop_front();
            if (r == x2 && c == y2) {
                cout << steps << endl;
                return 0;
            }
            for (auto [rd, cd] : dirs) {
                for (int moved = 1; moved <= k; moved++) {
                    int nr = r + (moved * rd);
                    int nc = c + (moved * cd);
                    if (nr < 0 || nr >= H || nc < 0 || nc >= W) {
                        continue;
                    }
                    if (grid[nr][nc] == '#') break;
                    if (minD[nr][nc] <= steps) break;
                    minD[nr][nc] = steps + 1;
                    if (!seen.contains({nr, nc})) {
                        seen.insert({nr, nc});
                        q.push_back({nr, nc});
                    }
                }
            }
        }
        steps++;
    }

    cout << -1 << endl;
}