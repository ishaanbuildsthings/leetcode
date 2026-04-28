#include <bits/stdc++.h>
using namespace std;

int MOD = 998244353;

void solve() {
    int l, r; cin >> l >> r;
    int cnt = 0;
    int cur = l;
    while (cur <= r) {
        cnt++;
        cur <<= 1;
    }
    // cnt = max set size, achieved by starting at some x and doubling (cnt-1) times
    int multiplier = (1 << (cnt - 1));

    // binary search for biggest x where x * 2^(cnt-1) <= r
    int left = l, right = r, res = l - 1;
    while (left <= right) {
        int m = (left + right) / 2;
        if ((long long)m * multiplier <= r) {
            res = m;
            left = m + 1;
        } else {
            right = m - 1;
        }
    }
    long long options = res - l + 1;

    // we could replace one doubling with a tripling
    // need x * 3 * 2^(cnt-2) <= r, and there are (cnt-1) positions to place the triple
    if (cnt >= 2) {
        int tripleMul = 3 * (1 << (cnt - 2));
        int left = l, right = r, res2 = l - 1;
        while (left <= right) {
            int m = (left + right) / 2;
            if ((long long)m * tripleMul <= r) {
                res2 = m;
                left = m + 1;
            } else {
                right = m - 1;
            }
        }
        long long tripleStarts = max(0, res2 - l + 1);
        options = (options + tripleStarts * (cnt - 1)) % MOD;
    }
    cout << cnt << " " << options % MOD << '\n';
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}