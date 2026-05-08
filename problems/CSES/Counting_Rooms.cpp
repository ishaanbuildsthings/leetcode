#include <bits/stdc++.h>
using namespace std;
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m;
    cin >> n >> m;
 
    vector<string> grid;
    for (int r = 0; r < n; r++) {
      string row;
      cin >> row;
      grid.push_back(row);
    }
 
    vector<vector<bool>> seen(n, vector<bool>(m, false));
 
    function<void(int, int)> dfs = [&](int r, int c) {
      if (r < 0 || r >= n || c < 0 || c >= m || seen[r][c] || grid[r][c] == '#') {
        return;
      }
      seen[r][c] = true;
      dfs(r + 1, c);
      dfs(r - 1, c);
      dfs(r, c + 1);
      dfs(r, c - 1);
    };
 
    int rooms = 0;
    for (int r = 0; r < n; r++) {
      for (int c = 0; c < m; c++) {
        if (grid[r][c] == '.' && !seen[r][c]) {
          dfs(r, c);
          rooms++;
        }
      }
    }
 
    cout << rooms << endl;
 
 
}
