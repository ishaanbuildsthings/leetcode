#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int MAX_N = 1000000;
const ll BASE = 911;
const ll MOD = 1000000007;

ll basePow[MAX_N + 1];


void init() {
    basePow[0] = 1;
    for (int p = 1; p <= MAX_N; p++) {
        ll nv = basePow[p - 1] * BASE % MOD;
        basePow[p] = nv;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    
    init();

    string s; cin >> s;
    int n = s.size();

    // build forward pf hash
    vector<ll> pfHash;
    ll hash = 0;
    for (int i = 0; i < n; i++) {
        int coeff = s[i] - 'a' + 1;
        hash *= BASE;
        hash += coeff;
        hash %= MOD;
        pfHash.push_back(hash);
    }

    auto forward = [&](int l, int r) -> ll {
        ll fullPf = pfHash[r];
        ll subtractedPf = l > 0 ? pfHash[l - 1] : 0LL;
        ll width = r - l + 1;
        subtractedPf *= basePow[width];
        subtractedPf %= MOD;
        ll ans = (fullPf - subtractedPf);
        if (ans < 0) ans += MOD;
        return ans;
    };

    // build reverse pf hash
    // big exponents on RIGHT
    // so abc would be a^0 + b^1 + c^2 is the hash of cba
    // so in our normal forward hash we have a^2 + b^1 + c^0 which means not a palindrome
    vector<ll> revHash(n); // revHash[i] is for the suffix i..., but REVERSED
    hash = 0;
    for (int i = n - 1; i >= 0; i--) {
        hash *= BASE;
        ll coeff = s[i] - 'a' + 1;
        hash += coeff;
        hash %= MOD;
        revHash[i] = hash;
    }

    // hash of the substring s[l...r] REVERSED
    auto backwards = [&](int l, int r) -> ll {
        ll fullHash = revHash[l]; // l...
        ll hashRight = r + 1 < n ? revHash[r + 1] : 0LL;
        int width = r - l + 1;
        hashRight *= basePow[width];
        hashRight %= MOD;
        fullHash -= hashRight;
        if (fullHash < 0) fullHash += MOD;
        return fullHash;
    };

    auto isPal = [&](int l, int r) -> bool {
        ll h1 = forward(l, r);
        ll h2 = backwards(l, r);
        return h1 == h2;
    };

    int resL = 0;
    int resR = 0;

    // try odd centers
    for (int i = 0; i < n; i++) {
        int leftSpots = i;
        int rightSpots = n - i - 1;
        int L = 0; // min wingspan
        int R = min(leftSpots, rightSpots); // max wingspots
        int resWingSpan = 0;
        while (L <= R) {
            int m = (L + R) / 2;
            int lidx = i - m;
            int ridx = i + m;
            if (isPal(lidx, ridx)) {
                resWingSpan = m;
                L = m + 1;
            } else {
                R = m - 1;
            }
        }
        if (2 * resWingSpan + 1 > (resR - resL + 1)) {
            resL = i - resWingSpan;
            resR = i + resWingSpan;
        }

        resWingSpan = 0;
        // try even center
        if (i < n - 1 && s[i] == s[i + 1]) {
            leftSpots = i;
            rightSpots = rightSpots - 1;
            L = 0;
            R = min(leftSpots, rightSpots);
            while (L <= R) {
                int m = (L + R) / 2;
                int lidx = i - m;
                int ridx = i + 1 + m;
                if (isPal(lidx, ridx)) {
                    resWingSpan = m;
                    L = m + 1;
                } else {
                    R = m - 1;
                }
            }
            if (2 * resWingSpan + 2 > (resR - resL + 1)) {
                resL = i - resWingSpan;
                resR = i + resWingSpan + 1;
            }
        }


    }

    for (int i = resL; i <= resR; i++) {
        cout << s[i];
    }


}