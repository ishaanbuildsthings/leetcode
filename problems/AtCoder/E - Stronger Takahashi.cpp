#include <bits/stdc++.h>
using namespace std;

vector<pair<int,int>> D = {
  {0,1},{0,-1},{1,0},{-1,0},{2,0},{-2,0},{0,2},{0,-2},{2,1},{2,-1},{1,2},{1,-2},{-2,-1},{-2,1},{-1,2},{-1,-2}
};
vector<pair<int,int>> D2 = {
  {0,1},{0,-1},{1,0},{-1,0}
};
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int h, w; cin >> h >> w;
  vector<string> grid;
  for (int i = 0; i < h; i++) {
    string row; cin >> row;
    grid.push_back(row);
  }
  using Node = tuple<int,int,int>; // (dist, r, c)
  deque<Node> q;
  int INF = 1 << 25;
  vector<vector<int>> minDists(h, vector<int>(w, INF));
  minDists[0][0] = 0;
  q.push_back({0, 0, 0});
  while (!q.empty()) {
    auto [dist, r, c] = q.front(); q.pop_front();
    if (minDists[r][c] != dist) continue;
    // try punched regions
    for (auto [rd, cd] : D) {
      int nr = r + rd;
      int nc = c + cd;
      if (nr < 0 || nr >= h || nc < 0 || nc >= w) {
        continue;
      }
      int nd = dist + 1;
      if (nd < minDists[nr][nc]) {
        minDists[nr][nc] = nd;
        q.push_back({nd, nr, nc});
      }
    }
    // try normal regions
    for (auto [rd, cd] : D2) {
      int nr = r + rd;
      int nc = c + cd;
      if (nr < 0 || nr >= h || nc < 0 || nc >= w) {
        continue;
      }
      if (grid[nr][nc] == '#') continue;
      int nd = dist;
      if (nd < minDists[nr][nc]) {
        minDists[nr][nc] = nd;
        q.push_front({nd, nr, nc});
      }
    }
  }
  cout << minDists[h-1][w-1] << endl;
}