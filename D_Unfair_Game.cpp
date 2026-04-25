#include <bits/stdc++.h>
using namespace std;

long long nCr(int n, int r) {
    if (r < 0 || r > n) return 0;
    if (r > n - r) r = n - r;
    long long res = 1;
    for (int i = 0; i < r; i++) {
        res = res * (n - i) / (i + 1);
    }
    return res;
}

void solve() {
    int n, k; cin >> n >> k;
    int d = __lg(n);
    // how many numbers from 1 to N require >K moves where they can halve it or subtract 1?
    long long aliceWins = 0;
    for (int msb = 0; msb < d; msb++) {
        int opsToZero = msb + 1;
        int zeroes = msb;
        int remainingOps = k - opsToZero; // how many ops alice has level
        if (remainingOps < 0) continue;
        int picks = min(remainingOps, zeroes);
        // we have `zeroes` positions to choose up to min(zeroes, remainingOps) options
        for (int pickAmt = 0; pickAmt <= picks; pickAmt++) {
            long long ways = nCr(zeroes, pickAmt);
            aliceWins += ways;
        }
    }
    // if alice picks exactly N, we can't pick other bits in that because it exceeds N
    
    if (d < k) {
        aliceWins++;
    }
    cout << n - aliceWins << endl;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) {
        solve();
    }
}