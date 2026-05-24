#include <bits/stdc++.h>
using namespace std;
using ll = long long;

struct RSQ1D {
  vector<vector<int>> rowPref, colPref;
  RSQ1D(const vector<vector<int>>& a) {
    int h = (int)a.size(), w = (int)a[0].size();
    rowPref.assign(h, vector<int>(w + 1, 0));
    for (int r = 0; r < h; r++)
      for (int c = 0; c < w; c++)
        rowPref[r][c + 1] = rowPref[r][c] + a[r][c];
    colPref.assign(w, vector<int>(h + 1, 0));
    for (int c = 0; c < w; c++)
      for (int r = 0; r < h; r++)
        colPref[c][r + 1] = colPref[c][r] + a[r][c];
  }
  inline int sumRow(int r, int c1, int c2) const { return rowPref[r][c2 + 1] - rowPref[r][c1]; }
  inline int sumCol(int c, int r1, int r2) const { return colPref[c][r2 + 1] - colPref[c][r1]; }
};

int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);

  int h, w; 
  cin >> h >> w;
  vector<vector<int>> grid(h, vector<int>(w));
  for (int r = 0; r < h; r++)
    for (int c = 0; c < w; c++)
      cin >> grid[r][c];

  const int NINF = -1000000000;

  RSQ1D q(grid);

  vector<vector<array<int,2>>> dpPrev(h, vector<array<int,2>>(w, {0,0}));
  vector<vector<array<int,2>>> dpCur(h, vector<array<int,2>>(w, {NINF,NINF}));

  ll res = NINF;
  int K = min(h, w);
  for (int steps = 3; steps <= K; steps += 2) {
    for (int r = 0; r < h; r++) {
      for (int c = 0; c < w; c++) dpCur[r][c] = {NINF, NINF};
    }

    for (int r = 0; r < h; r++) {
      for (int c = 0; c < w; c++) {
        int c2 = c + steps - 1, r2 = r + steps - 1;
        if (c2 >= w || r2 >= h) break;
        ll right = q.sumRow(r, c, c2);
        ll down  = q.sumCol(c2, r, r2);
        ll left  = q.sumRow(r2, c, c2);
        ll init  = right + down + left - grid[r][c2] - grid[r2][c2];
        ll resHere = init + dpPrev[r2][c][1];
        if (resHere > res) res = resHere;
      }
    }

    int dr = steps - 1, dc = steps - 1;

    for (int r = dr; r < h; r++) {
      int r2 = r - dr;
      for (int c = 0; c + dc < w; c++) {
        int c2 = c + dc;
        ll score = 0;
        score += q.sumCol(c, r2, r);
        score += q.sumRow(r2, c, c2);
        score -= grid[r][c];
        score -= grid[r2][c];
        int tail = dpPrev[r2][c2][0];
        if (tail == NINF) dpCur[r][c][1] = NINF;
        else dpCur[r][c][1] = (int)(score + tail);
      }
    }

    for (int r = 0; r + dr < h; r++) {
      int r2 = r + dr;
      for (int c = dc; c < w; c++) {
        int c2 = c - dc;
        ll score = 0;
        score += q.sumCol(c, r, r2);
        score += q.sumRow(r2, c2, c);
        score -= grid[r][c];
        score -= grid[r2][c];
        int tail = dpPrev[r2][c2][1];
        if (tail == NINF) dpCur[r][c][0] = NINF;
        else dpCur[r][c][0] = (int)(score + tail);
      }
    }

    dpPrev.swap(dpCur);
  }

  cout << res << "\n";
  return 0;
}