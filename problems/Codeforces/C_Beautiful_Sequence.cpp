#include <bits/stdc++.h>
using namespace std;
const int MOD = 998244353;


void solve() {
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    int mx = *max_element(A.begin(), A.end());
    int mn = *min_element(A.begin(), A.end());
    if (mn != 1 || mx != 3) {
        cout << 0 << endl;
        return;
    }

    vector<vector<int>> cache(n, vector<int>(4, -1));
    // How many sequences can we form in i... if we have taken an X before
    auto dp = [&](auto&& self, int i, int taken) -> int {
        if (i == A.size()) {
            return (taken == 3 ? 1 : 0);
        }
        if (cache[i][taken] != -1) {
            return cache[i][taken];
        }
        int num = A[i];
        bool canTake = false;
        if (taken == 2 && num == 2) {
            canTake = true;
        }
        if (num == taken + 1) {
            canTake = true;
        }
        // skip
        int resHere = self(self, i + 1, taken);
        if (canTake) {
            int take = self(self, i + 1, num);
            resHere += take;
            resHere %= MOD;
        }
        cache[i][taken] = resHere;
        return resHere;
    };
    cout << dp(dp, 0, 0) << endl;

}
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}