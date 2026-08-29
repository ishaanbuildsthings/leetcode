#include <bits/stdc++.h>
using namespace std;
using ll = long long;
ll MOD = 1000000007;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;

    vector<ll> dp(k + 1, 0); // # of ways to make a permutation of size N with this many inversions
    vector<ll> ndp(k + 1, 0);
    dp[0] = 1;
    for (int i = 1; i <= n; i++) {
        // each new way wtih some K is the sum of the previous `i` values

        vector<ll> pf(k + 1, 0);
        ll curr = 0;
        for (int j = 0; j <= k; j++) {
            curr += dp[j];
            if (curr >= MOD) curr -= MOD;
            pf[j] = curr;
        }

        auto query = [&](int l, int r) -> ll {
            ll ans = pf[r] - (l > 0 ? pf[l - 1] : 0);
            if (ans < 0) ans += MOD;
            if (ans >= MOD) ans -= MOD;
            return ans;
        };

        for (int j = 0; j <= k; j++) {
            int L = max(0, j - i + 1);
            int R = j;
            ll tot = query(L, R);
            ndp[j] = tot;
        }

        swap(dp, ndp);
    }

    cout << dp[k];
}