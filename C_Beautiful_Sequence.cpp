#include <bits/stdc++.h>
using namespace std;
const int MOD = 998244353;


void solve() {
    // cout << "=========" << endl;
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    // for (auto x : A) cout << x << " ";
    // cout << endl;
    int mx = *max_element(A.begin(), A.end());
    int mn = *min_element(A.begin(), A.end());
    if (mn != 1 || mx != 3) {
        // cout << "no solutions found due to max and min" << endl;
        cout << 0 << endl;
        return;
    }

    vector<vector<int>> cache(n, vector<int>(4, -1));
    // How many sequences can we form in i... if we have taken an X before
    auto dp = [&](auto&& self, int i, int taken) -> int {
        // cout << "dp called on i=" << i << " taken=" << taken << endl;
        if (i == A.size()) {
            // cout << "base case hit, ret: " << (taken == 3 ? 1 : 0) << endl;
            return (taken == 3 ? 1 : 0);
        }
        if (cache[i][taken] != -1) {
            return cache[i][taken];
        }
        int num = A[i];
        // cout << "num is: " << num << endl;
        bool canTake = false;
        if (taken == 2 && num == 2) {
            canTake = true;
        }
        if (num == taken + 1) {
            canTake = true;
        }
        // bool canTake = (num == taken || num == taken + 1);
        // cout << "we can take: " << canTake << endl;
        // skip
        int resHere = self(self, i + 1, taken);
        if (canTake) {
            int take = self(self, i + 1, num);
            resHere += take;
            resHere %= MOD;
        }
        cache[i][taken] = resHere;
        // cout << "THE ANSWER AT I=" << i << " TAKEN=" << taken << " IS: " << resHere << endl;
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