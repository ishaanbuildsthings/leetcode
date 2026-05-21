#include <bits/stdc++.h>
using namespace std;

int arr[100000];

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
      int n, m;
      cin >> n >> m;
      for (int i = 0; i < n; i++) {
        cin >> arr[i];
      }

      int reqIndex = -1;
      for (int i = n - 1; i >= 0; i--) {
        if (arr[i] != i + 1) {
          reqIndex = i;
          break;
        }
      }

      // cout << "req index: " << reqIndex << endl;
      // chance of success is 1-chance of failure
      // chance of failure is E[e_0 * e_1 * e_2 * ...] where e_i is the chance the ith event fails to sort the entire prefix
      // multiply independent events is E[e_0] * E[e_1] * ...

      double fail = 1.0;
      for (int i = 0; i < m; i++) {
        double p;
        int r;
        cin >> r >> p;
        if (r < reqIndex + 1) {
          continue;
        }
        fail *= (1.0 - p);
      }

      if (reqIndex == -1) {
        cout << 1 << endl;
      } else {
        cout << fixed << setprecision(6) << (1.0 - fail) << endl;
      }

    }

    return 0;
}