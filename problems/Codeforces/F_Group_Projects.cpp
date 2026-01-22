#include <bits/stdc++.h>
using namespace std;
const int MOD = 1000000000 + 7;
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k; cin >> n >> k;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    sort(A.begin(), A.end());
    // dp[open][penaltySoFar] -> ways
    vector<vector<int>> dp(n + 1, vector<int>(k + 1, 0));
    dp[0][0] = 1;
    for (int i = 0; i < n; i++) {
        int num = A[i];
        int diff = i + 1 < n ? A[i + 1] - A[i] : 0;
        vector<vector<int>> ndp(n + 1, vector<int>(k + 1, 0));
        for (int oldOpen = 0; oldOpen <= i; oldOpen++) {
            for (int oldP = 0; oldP <= k; oldP++) {
                // put in their own group
                int p1 = oldP + 1LL * oldOpen * diff;
                if (p1 <= k) {
                    ndp[oldOpen][p1] += dp[oldOpen][oldP];
                    ndp[oldOpen][p1] %= MOD;
                }
                // start a new group
                int p2 = oldP + (1LL * (oldOpen + 1) * diff);
                if (p2 <= k) {
                    ndp[oldOpen + 1][p2] += dp[oldOpen][oldP];
                    ndp[oldOpen + 1][p2] %= MOD;
                }
                // close an existing group
                if (oldOpen) {
                    int p3 = oldP + (1LL * (oldOpen - 1) * diff);
                    if (p3 <= k) {
                        ndp[oldOpen - 1][p3] += (1LL * dp[oldOpen][oldP] * oldOpen) % MOD;
                        ndp[oldOpen - 1][p3] %= MOD;
                    }
                }
                // add to existing group
                int p4 = oldP + (1LL * oldOpen * diff);
                if (p4 <= k) {
                    ndp[oldOpen][p4] += (1LL * dp[oldOpen][oldP] * oldOpen) % MOD;
                    ndp[oldOpen][p4] %= MOD;
                }
            }
        }
        dp = ndp;
    }
    long long out = 0;
    for (int p = 0; p <= k; p++) {
        out += dp[0][p];
        out %= MOD;
    }
    cout << out;

}