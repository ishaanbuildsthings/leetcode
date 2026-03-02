#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, g; cin >> n >> g;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];

    ll tot = 0;
    vector<ll> pf;
    for (auto x : arr) {
        tot += x;
        pf.push_back(tot);
    }
    auto cost = [&](int l, int r) -> ll {
        int width = r - l + 1;
        ll total = pf[r] - (l > 0 ? pf[l - 1] : 0);
        return 1LL * width * total;
    };
    vector<ll> dp(n); // dp[i] is the cost for 0...i into 1 partition
    for (int i = 0; i < n; i++) {
        dp[i] = cost(0, i);
    }
    vector<ll> ndp(n);
    for (int p = 2; p <= g; p++) {
        auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
            if (fillL > fillR) return;
            int mid = (fillL + fillR) / 2;
            ll best = LLONG_MAX;
            int bestJ = -1;
            for (int j = leftJ; j <= min(mid, rightJ); j++) {
                ll ans = cost(j, mid) + (j > 0 ? dp[j - 1] : 0);
                if (ans < best) {
                    best = ans;
                    bestJ = j;
                }
            }
            ndp[mid] = best;
            self(self, fillL, mid - 1, leftJ, bestJ);
            self(self, mid + 1, fillR, bestJ, rightJ);
        };
        solve(solve, 0, n - 1, 0, n - 1);
        swap(dp, ndp);
    }
    cout << dp[n - 1] << '\n';
}