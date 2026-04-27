#include <bits/stdc++.h>
using namespace std;

void solve() {
    long long n, x; cin >> n >> x;
    // we need to find the smallest number M where n & n + 1 & ... & M = x
    // the AND can only go down
    // so if n < x already we fail

    if (n < x) {
        cout << -1 << endl;
        return;
    }

    auto rangeAnd = [&](long long L, long long R) -> long long {
        int shifts = 0;
        while (L < R) {
            L >>= 1;
            R >>= 1;
            shifts++;
        }
        return L << shifts;
    };

    long long left = n;
    long long right = LLONG_MAX / 4;
    long long res = -1;
    while (left <= right) {
        long long m = (left + right) / 2;
        auto rangedAnd = rangeAnd(n, m);
        if (rangedAnd == x) {
            res = m;
            right = m - 1;
        } else if (rangedAnd < x) {
            right = m - 1;
        } else {
            left = m + 1;
        }
    }
    if (res == -1) {
        cout << -1 << endl;
    } else {
        cout << res << endl;
    }
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}