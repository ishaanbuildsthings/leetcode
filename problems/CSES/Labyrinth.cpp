#include <bits/stdc++.h>
using namespace std;
 
pair<int, int> dirs[4] = {{1,0},{-1,0},{0,1},{0,-1}};
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
    pair<int, int> S{-1, -1}, T{-1, -1};
    vector<string> grid;
    for (int r = 0; r < n; r++) {
      string row;
      cin >> row;
      grid.push_back(row);
      for (int c = 0; c < m; c++) {
        if (grid[r][c] == 'A') {
          S = {r, c};
        } else if (grid[r][c] == 'B') {
          T = {r, c};
        }
      }
    }
 
     // par[r][c] = {pR, pC}
     vector<vector<pair<int,int>>> par(n, vector<pair<int,int>>(m, {-1, -1}));
 
     queue<pair<int, int>> q;
     q.push({S.first, S.second});
     grid[S.first][S.second] = 'S';
     while (!q.empty()) {
      int length = q.size();
      for (int i = 0; i < length; i++) {
        auto [r, c] = q.front();
        q.pop();
        for (auto [rDiff, cDiff] : dirs) {
          int nr = r + rDiff;
          int nc = c + cDiff;
          if (nr < 0 || nr == n || nc < 0 || nc == m) continue; // skip out of bounds
          if (grid[nr][nc] == 'S') continue; // skip seen
          if (grid[nr][nc] == '#') continue; // skip walls
          grid[nr][nc] = 'S';
          q.push({nr, nc});
          par[nr][nc] = {r, c};
        }
      }
     }
     if (par[T.first][T.second] == pair<int,int>{-1, -1}) {
      cout << "NO" << endl;
      return 0;
     }
 
    string path;
    for (auto cur = T; cur != S; cur = par[cur.first][cur.second]) {
        auto p = par[cur.first][cur.second];
        if (cur.first == p.first + 1) path.push_back('D');
        else if (cur.first == p.first - 1) path.push_back('U');
        else if (cur.second == p.second + 1) path.push_back('R');
        else path.push_back('L');
    }
    reverse(path.begin(), path.end());
 
    cout << "YES\n" << path.size() << '\n' << path << '\n';
 
}