#include <bits/stdc++.h>
using namespace std;

using ll = long long;
const ll MOD = 1000000000 + 7;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int k, n; cin >> n >> k;
    vector<ll> modFac = {1};
    for (int fac = 1; fac <= n; fac++) {
        modFac.push_back((fac * modFac.back()) % MOD);
    }
    vector<ll> invFac(n + 1, 0);
    auto modPow = [&](auto&& self, ll base, ll e) -> ll {
        if (e == 0) return 1LL;
        if (e % 2) {
            return (base * self(self, base, e - 1)) % MOD;
        }
        ll half = self(self, base, e / 2);
        return (half * half) % MOD;
    };
    invFac[n] = modPow(modPow, modFac[n], MOD - 2);
    for (int i = n; i >= 1; i--) invFac[i - 1] = (invFac[i] * i) % MOD;
    
    auto nCk = [&](int nn, int k) -> ll {
        ll numerator = modFac[nn];
        ll d1 = invFac[nn - k];
        ll d2 = invFac[k]; // dedupe permutation
        return (((numerator * d1) % MOD) * d2) % MOD;
    };
    ll ways = modPow(modPow, k, n); // ways to make sequences of length N using K characters, but can be missing
    // We need to exclude things missing 1 number type, 2 types, and so on
    for (int sz = 1; sz <= k; sz++) {
        bool shouldSubtract = (sz % 2) == 1; // inclusion-exclusion
        ll combos = nCk(k, sz);
        ll waysWithThoseGone = modPow(modPow, k - sz, n);
        ll total = (combos * waysWithThoseGone) % MOD;
        if (shouldSubtract) {
            ways -= total;
        } else {
            ways += total;
        }
        if (ways < 0) ways += MOD;
        ways %= MOD;
    }
    cout << ways << endl;
}