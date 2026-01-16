#include <bits/stdc++.h>
using namespace std;
 
int main() {
  ios::sync_with_stdio(false);
  cin.tie(nullptr);
  int n, q;
  cin >> n >> q;
  int LOG = 32 - __builtin_clz(1000000000);
  vector<vector<int>> up(LOG, vector<int>(n + 1));
  for (int i = 0; i < n; i++) {
    int nxt;
    cin >> nxt;
    up[0][i + 1] = nxt;
  }
  for (int k = 1; k < LOG; k++) {
    for (int node = 1; node <= n; node++) {
      int mid = up[k-1][node];
      up[k][node] = up[k-1][mid];
    }
  }
  for (int i = 0; i < q; i++) {
    int planet, teleporters;
    cin >> planet >> teleporters;
    for (int k = 0; k < LOG; k++) {
      if (teleporters >> k & 1) planet = up[k][planet];
    }
    cout << planet << endl;
  }
}
