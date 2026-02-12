#include <bits/stdc++.h>
using namespace std;
const int MOD = 1000000000 + 7;
int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;
    vector<pair<int,int>> traps(m); for (int i = 0; i < m; i++) {
        int x, y;
        cin >> x >> y;
        pair<int, int> p = {x, y};
        traps[i] = p;
    }
    traps.push_back({n, n});
    m = traps.size();
    vector<long long> modFac = {1};
    for (long long fac = 1; fac <= 2000000 + 5; fac++) {
        long long newTerm = (modFac.back() * fac) % MOD;
        modFac.push_back(newTerm);
    }
    vector<long long> invFac(modFac.size());
    auto modPow = [&](long long a, long long e) -> long long {
        long long res = 1;
        while (e) {
            if (e & 1) res = res * a % MOD;
            a = a * a % MOD;
            e >>= 1;
        }
        return res;
    };
    
    invFac.back() = modPow(modFac.back(), MOD - 2);
    for (int i = (int)modFac.size() - 2; i >= 0; i--) {
        invFac[i] = invFac[i + 1] * (i + 1) % MOD;
    }
    
    auto nCk = [&](int n, int k) -> long long {
        long long numerator = modFac[n];
        long long d1 = invFac[n - k];
        long long d2 = invFac[k];
        return (((numerator * d1) % MOD) * d2) % MOD;
    };


    auto ways = [&](int r1, int c1, int r2, int c2) -> long long {
        int height = r2 - r1;
        int width = c2 - c1;
        return nCk(height + width, height);
    };

    vector<long long> dp(m, 0);
    sort(traps.begin(), traps.end());
    dp[0] = ways(1, 1, traps[0].first, traps[0].second);
    for (int i = 1; i < m; i++) {
        long long bigWays = ways(1, 1, traps[i].first, traps[i].second);
        for (int prev = 0; prev < i; prev++) {
            if (traps[prev].second > traps[i].second) continue;
            long long prevCombos = (dp[prev] * ways(traps[prev].first, traps[prev].second, traps[i].first, traps[i].second)) % MOD;
            bigWays -= prevCombos;
            if (bigWays < 0) bigWays += MOD;
        }
        dp[i] = bigWays;
    }
    cout << dp.back() << endl;
}