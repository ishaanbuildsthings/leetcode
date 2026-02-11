#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    string s; cin >> s;
    int n = s.size();
    long long MOD = 1000000000 + 7;
    vector<long long> modFac = {1};
    for (int fac = 1; fac <= n; fac++) {
        long long term = (fac * modFac.back()) % MOD;
        modFac.push_back(term);
    }
    auto modPow = [&](long long base, long long exp) -> long long {
        long long res = 1;
        while (exp) {
            if (exp & 1) res = res * base % MOD;
            base = base * base % MOD;
            exp >>= 1;
        }
        return res;
    };
    vector<long long> invFac(n + 1);
    invFac[n] = modPow(modFac[n], MOD - 2);
    for (int i = n; i > 0; i--) {
        invFac[i - 1] = invFac[i] * i % MOD;
    }
    auto interleave = [&](int a, int b) -> long long {
        return modFac[a + b] * invFac[a] % MOD * invFac[b] % MOD;
    };
    vector<vector<long long>> cache(n, vector<long long>(n, -1));
    auto dp = [&](auto&& self, int l, int r) -> long long {
        if (l == r) return 0;
        if (l > r) return 1;
        if (cache[l][r] != -1) return cache[l][r];
        long long resHere = 0;
        for (int i = l + 1; i <= r; i++) {
            if (s[i] == s[l]) {
                // pruning
                if (((i - 1) - (l + 1) + 1) & 1) continue;
                if ((r - (i + 1) + 1) & 1) continue;
                int rightWidth = (r - (i + 1) + 1) / 2;
                int leftInsideWidth = (i - (l + 1)) / 2;
                long long leftWays = self(self, l + 1, i - 1);
                long long rightWays = self(self,  i + 1, r);
                long long interleaveWays = interleave(leftInsideWidth + 1, rightWidth);
                resHere += ((leftWays * rightWays) % MOD * interleaveWays) % MOD;
                resHere %= MOD;
            }
        }
        cache[l][r] = resHere;
        return resHere;
    };
    cout << dp(dp, 0, n - 1) << endl;
}