#include <bits/stdc++.h>
using namespace std;
using ll = long long;

void solve() {
    int n; cin >> n;
    vector<ll> xs(n); for (int i = 0; i < n; i++) cin >> xs[i];
    vector<ll> ys(n); for (int i = 0; i < n; i++) cin >> ys[i];

    const ll INF = LLONG_MAX / 4;

    vector<vector<ll>> cache(n + 1, vector<ll>(2, INF)); // cache[i][onLeft] -> res or INF

    // the max surplus from the perspective of whoever is on the left?
    auto dp = [&](auto&& self, int i, int sunnyOnLeft) -> ll {
        if (i == n) return 0;
        if (cache[i][sunnyOnLeft] != INF) {
            return cache[i][sunnyOnLeft];
        }

        ll left = xs[i];
        ll right = ys[i];

        if (sunnyOnLeft) {
            ll leftSurplus = left - right;
            // sunny can buy and stay
            ll ifBuy = leftSurplus + self(self, i + 1, 1);
            ll ifSkip = -self(self, i + 1, 0);
            ll ans = max(ifBuy, ifSkip);
            cache[i][sunnyOnLeft] = ans;
            return ans;
        } else {
            // aubrey on left
            ll leftSurplus = left - right;
            ll ifBuy = leftSurplus + self(self, i + 1, 1);
            ll ifSkip = -self(self, i + 1, 0);
            ll ans = max(ifBuy, ifSkip);
            cache[i][sunnyOnLeft] = ans;
            return ans;
        }
    };

    ll ans = dp(dp, 0, 1);
    // cout << ans << endl;
    if (ans > 0) {
        cout << "Sunny" << endl;
    } else if (ans == 0) {
        cout << "Draw" << endl;
    } else {
        cout << "Aubrey" << endl;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}