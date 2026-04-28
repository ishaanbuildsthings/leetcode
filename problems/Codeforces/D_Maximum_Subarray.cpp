#include <bits/stdc++.h>
using namespace std;

constexpr int MAX_N = 200000;
constexpr int MAX_K = 20;
bool visited[MAX_N][MAX_K + 1][2];
long long cache[MAX_N][MAX_K + 1][2]; // dp[i][opsLeft][state] is the answer for that

constexpr long long NEG_INF = LLONG_MIN / 2;

void solve() {
    int n, k, x; cin >> n >> k >> x;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j <= k; j++) {
            for (int z = 0; z < 2; z++) {
                visited[i][j][z] = false;
            }
        }
    }
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];

    auto dp = [&](auto&& self, int i, int opsLeft, int state) -> long long {
        if (i == n) {
            if (opsLeft) return NEG_INF;
            return 0;
        }
        if (visited[i][opsLeft][state]) return cache[i][opsLeft][state];

        int remainingElements = n - i - 1;
        int v = A[i];
        long long res = NEG_INF;
        // haven't started the array yet
        if (state == 0) {
            auto ifSkipNoReplace = self(self, i + 1, opsLeft, 0);
            auto ifSkipAndReplace = opsLeft ? self(self, i + 1, opsLeft - 1, 0) : NEG_INF;
            auto startNoReplace = (v - x) + self(self, i + 1, opsLeft, 1);
            long long startAndStopNoReplace = opsLeft <= remainingElements ? (v - x) : NEG_INF;
            res = max({res, ifSkipAndReplace, ifSkipNoReplace, startNoReplace, startAndStopNoReplace});
            if (opsLeft) {
                auto startAndReplace = (v + x) + self(self, i + 1, opsLeft - 1, 1);
                // needed when we never have any operations I guess
                long long startAndStopWithReplace = (opsLeft - 1) <= remainingElements ? (v + x) : NEG_INF;
                res = max({res, startAndReplace, startAndStopNoReplace, startAndStopWithReplace});
            }
        } else if (state == 1) {
            auto continueNoReplace = v - x + self(self, i + 1, opsLeft, 1);
            long long stopHereNoReplace = opsLeft <= remainingElements ? (v - x) : NEG_INF;
            
            res = max(stopHereNoReplace, continueNoReplace);
            if (opsLeft) {
                bool canReplaceAndStop = (opsLeft - 1) <= remainingElements;
                long long replaceAndStop = canReplaceAndStop ? (v + x) : NEG_INF;
                auto replaceAndContinue = v + x + self(self, i + 1, opsLeft - 1, 1);
                res = max({res, replaceAndStop, replaceAndContinue});
            }
        }
        visited[i][opsLeft][state] = true;
        cache[i][opsLeft][state] = res;
        return res;
    };

    auto ans = dp(dp, 0, k, 0);

    cout << ans << '\n';
}
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int t; cin >> t;
    while (t--) solve();
}