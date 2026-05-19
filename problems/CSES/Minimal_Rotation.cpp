#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll BASE = 911;
const ll MOD = 1000000007;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    string doubled = s + s;
    int n = s.size();
    int N = doubled.size();

    vector<ll> basePow(N + 1);
    basePow[0] = 1;
    for (int p = 1; p <= N; p++) {
        ll nhash = (basePow[p - 1] * BASE) % MOD;
        basePow[p] = nhash;
    }
    vector<ll> pf;
    ll h = 0;
    for (auto c : doubled) {
        int coeff = c - 'a' + 1;
        h *= BASE;
        h += coeff;
        h %= MOD;
        pf.push_back(h);
    }

    auto getHash = [&](int l, int r) -> ll {
        ll fullHash = pf[r];
        ll left = l > 0 ? pf[l - 1] : 0LL;
        left *= basePow[r - l + 1];
        left %= MOD;
        ll ans = fullHash - left;
        if (ans < 0) ans += MOD;
        return ans;
    };

    auto lcp = [&](int L, int R, int A, int B) -> int {
        int l = 1;
        int width = R - L + 1;
        int r = width;
        int res = 0;
        while (l <= r) {
            int m = (l + r) / 2;
            ll h1 = getHash(L, L + m - 1);
            ll h2 = getHash(A, A + m - 1);
            if (h1 == h2) {
                res = m;
                l = m + 1;
            } else {
                r = m - 1;
            }
        }
        return res;
    };

    int resL = 0;
    for (int l = 0; l < n; l++) {
        // cout << "=======" << endl;
        int L1 = resL;
        int R1 = L1 + n - 1;

        int L2 = l;
        int R2 = l + n - 1;

        auto lcpVal = lcp(L1, R1, L2, R2);

        // cout << "lcp val: " << lcpVal << "at L1=" << L1 << " L2=" << L2 << endl;
        // cout << "res l is: " << resL << endl;
        int nxt1 = L1 + lcpVal; // first unmatched
        int nxt2 = L2 + lcpVal;

        if (nxt2 < doubled.size()) {
            char c1 = doubled[nxt1];
            char c2 = doubled[nxt2];
            // cout << "c1: " << c1 << " c2: " << c2 << endl;
            if (c2 < c1) {
                // cout << "updating resL to: " << l << endl;
                resL = l;
            }
        }
    }
    for (int i = resL; i < resL + n; i++) {
        cout << doubled[i];
    }
}