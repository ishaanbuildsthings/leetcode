#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const ll MOD = 998244353;

ll modAdd(ll a, ll b) {
    return (a + b) % MOD;
}

ll modMul(ll a, ll b) {
    return (a * b) % MOD;
}

ll modPow(ll base, ll exp, ll mod) {
    ll result = 1;
    base %= mod;
    while (exp > 0) {
        if (exp & 1) result = result * base % mod;
        base = base * base % mod;
        exp >>= 1;
    }
    return result;
}

ll modDiv(ll a, ll b) {
    return (a * modPow(b, MOD - 2, MOD)) % MOD;
}

void solve() {
    int n;
    cin >> n;
    vector<ll> A(n), B(n);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < n; i++) cin >> B[i];
    // for each pair of number positions we need to find the expected number of inversions

    // so for each pair we get an aLeft and aRight
    // i then have a required ratio, i need a pair of b numbers that is greater than aRight / aLeft

    // e.g. A is: [2, 5]
    // we need some B pair > 5/2 to produce an inversion

    vector<pair<ll, ll>> inversions;
    for (int i = 0; i < n; i++) {
        for (int j = i + 1; j < n; j++) {
            ll a1 = A[i];
            ll a2 = A[j];
            ll g = __gcd(a1, a2);
            a1 /= g;
            a2 /= g;
            inversions.push_back({a2, a1});
        }
    }

    // is the irreducible factor a bigger than b?
    auto isABigger = [](const pair<ll, ll>& a, const pair<ll, ll>& b) {
        ll aside = a.first * b.second;
        ll bside = b.first * a.second;
        return aside > bside;
    };

    auto cmp = [&](const pair<ll, ll>& a, const pair<ll, ll>& b) {
        // returns true if a should come before b (i.e., a < b)
        if (isABigger(b, a)) return true;
        return false;
    };

    sort(inversions.begin(), inversions.end(), cmp);

    // now for all n^2 inversions I need to see how many pairs of numbers fit that
    // so I could loop on n^2 inversions, then n first numbers, then binary search on n second numbers
    // n^3 log n

    // or we could loop on each pair of numbers, (i, j) and (j, i) are different (and chosen with equal chance)
    // for each ordered pair, we check the # of inversions it makes with a binary search on the n^2 requirements

    ll inversionsFound = 0;

    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            if (i == j) continue;

            // how many inversions are we strictly greater than?
            // find rightmost that we are strictly bigger than
            int l = 0;
            int r = (int)inversions.size() - 1;
            int resI = -1;
            while (l <= r) {
                int m = (r + l) / 2;
                const auto& inv = inversions[m];
                if (B[i] * inv.second > inv.first * B[j]) {
                    resI = m;
                    l = m + 1;
                } else {
                    r = m - 1;
                }
            }
            if (resI != -1) {
                ll beaten = resI + 1;
                inversionsFound = modAdd(inversionsFound, beaten);
            }
        }
    }

    inversionsFound %= MOD;
    ll totalPairs = modMul(n, n - 1);

    cout << modDiv(inversionsFound, totalPairs) << "\n";
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int t;
    cin >> t;
    while (t--) {
        solve();
    }
    return 0;
}