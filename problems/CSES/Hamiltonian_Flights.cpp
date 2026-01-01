#include <bits/stdc++.h>
using namespace std;
int MOD = 1000000007;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<vector<int>> g(n); // g[node1] holds a list of edges
    for (int i = 0; i < m; i++) {
        int a, b;
        cin >> a >> b;
        g[a-1].push_back(b-1);
    }
    int fmask = (1 << n) - 1;
    vector<vector<int>> dp(fmask + 1, vector<int>(n , 0)); // dp[completeMask][justArrived] is the number of ways to reach that state
    dp[1][0] = 1;

    for (int oldMask = 1; oldMask < fmask; oldMask++) {
        if ((oldMask & (1 << (n - 1))) && oldMask != fmask) continue; // skip masks that reached the final node early
        for (int justArrived = 0; justArrived < n; justArrived++) {
            if (!(oldMask & (1 << justArrived))) continue; // impossible state
            for (int outgoing : g[justArrived]) {
                if (oldMask & (1 << outgoing)) continue; // don't revisit nodes
                int nmask = oldMask | (1 << outgoing);
                if (outgoing == n - 1 && nmask != fmask) continue; // prune, don't reach final node early
                dp[nmask][outgoing] += dp[oldMask][justArrived];
                dp[nmask][outgoing] %= MOD;
            }
        }
    }
    cout << dp[fmask][n-1];


}