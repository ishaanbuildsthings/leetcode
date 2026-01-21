#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, m; cin >> n >> m;

    vector<int> spf(n + 1, 0); // spf[1] = 0, spf[prime] = prime
    for (int div = 2; div <= n; div++) {
        if (spf[div]) continue;
        spf[div] = div;
        for (long long mult = 1LL * div * div; mult <= n; mult += div) {
            if (spf[mult] == 0) spf[mult] = div;
        }
    }

    auto primeFactorize = [&](int x) -> vector<pair<int,int>> {
        vector<pair<int,int>> pfs;
        int cur = x;
        while (cur > 1) {
            int p = spf[cur];
            int e = 0;
            while (cur % p == 0) {
                e++;
                cur /= p;
            }
            pfs.push_back({p, e});
        }
        return pfs;
    };

    auto pfsToFacs = [&](vector<pair<int,int>>& pfs) -> vector<int> {
        vector<int> facs = {1};
        for (auto [p, e] : pfs) {
            int primePow = 1;
            int cSize = facs.size();
            for (int usedE = 1; usedE <= e; usedE++) {
                primePow *= p;
                for (int i = 0; i < cSize; i++) {
                    facs.push_back(primePow * facs[i]);
                }
            }
        }
        return facs;
    };

    vector<long long> dp(n + 1);
    dp[1] = 1;
    long long sumOverDivs = 0;
    long long pf = 1;
    for (int x = 2; x <= n; x++) {
        long long newWays = pf;
        auto pfs = primeFactorize(x);
        vector<int> facs = pfsToFacs(pfs);
        for (auto fac : facs) {
            if (fac == 1) continue; // not allowed to divide by 1
            if (fac == x) {
                sumOverDivs += dp[1]; // we always add a new way to divide by ourself
                sumOverDivs %= m;
                continue;
            }
            // proper divisor
            int q = x / fac;
            int oldQ = q - 1;
            sumOverDivs -= dp[oldQ];
            sumOverDivs += dp[q];
            if (sumOverDivs < 0) sumOverDivs += m;
            sumOverDivs %= m;
        }
        newWays += sumOverDivs;
        newWays %= m;
        dp[x] = newWays;
        pf += newWays;
        pf %= m;
    }

    cout << dp[n];
}

// 6 -> 3, 2, 1, 1, 1 (2, 3, 4, 5, 6)
// 7 -> 3, 2, 1, 1, 1, 1 (2, 3, 4, 5, 6, 7)
// 8 -> 4, 2, 2, 1, 1, 1, 1 (2, 3, 4, 5, 6, 7, 8)

// We always add 1 for the new number itself as a factor, like 8 is a factor of 8 and we add 1
// Every proper divisor of 8 (2, 4) increment by 1