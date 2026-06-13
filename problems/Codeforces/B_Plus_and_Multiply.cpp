#include <bits/stdc++.h>
using namespace std;


int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t;
    cin >> t;
    while (t--) {
      long n, a, b;
      cin >> n >> a >> b;

      if (a == 1) {
        long long diff = n - 1;
        if (diff % b == 0) {
          cout << "Yes" << endl;
        } else {
          cout << "No" << endl;
        }
        continue;
      }

      // for each multiplication of a, does it differ with n by a factor of b?
      long long curr = 1;
      bool found = false;
      while (curr <= n) {
        long long diff = n - curr;
        if (diff % b == 0) {
          cout << "Yes" << endl;
          found = true;
          break;
        }
        curr *= a;
      }
      if (!found) {
        cout << "No" << endl;
      }
    }

    return 0;
}