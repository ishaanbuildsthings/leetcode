#include <bits/stdc++.h>
using namespace std;

constexpr int MOD = 1000000007;

void solve() {
    int n, k; cin >> n >> k;
    int rowsTaken = 0;
    vector<pair<int,int>> moves(k);
    for (int i = 0; i < k; i++) {
        int r, c; cin >> r >> c;
        moves[i] = {r, c};
        if (r == c) {
            rowsTaken++;
        } else {
            rowsTaken += 2;
        }
    }
    // cerr << "init rows taken: " << rowsTaken << endl;
    vector<int> cache(n + 1, -1);
    auto dp = [&](auto&& self, int rowsLeft) -> int {
        // cout << "dp called on: " << rowsLeft << endl;
        if (rowsLeft == 0) return 1;
        int& cval = cache[rowsLeft];
        if (cval != -1) return cval;
        int placeOnLine = self(self, rowsLeft - 1);
        int colOptions = rowsLeft - 1;
        long long optsOnCol = (long long)colOptions * self(self, rowsLeft - 2);
        optsOnCol %= MOD;
        optsOnCol *= 2;
        optsOnCol %= MOD;
        cval = (optsOnCol + placeOnLine) % MOD;
        // cout << "returning: " << cval << " for rows left: " << rowsLeft << endl;
        return cval;
    };

    auto ans = dp(dp, n - rowsTaken);
    cout << ans << endl;

}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}