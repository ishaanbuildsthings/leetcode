#include <bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, m; cin >> n >> m;
    vector<int> A(n);
    vector<int> B(m);
    for (int i = 0; i < n; i++) cin >> A[i];
    for (int i = 0; i < m; i++) cin >> B[i];

    vector<vector<int>> dp(n + 1, vector<int>(m + 1)); // dp[i][j] is LCS for ...i-1 ...j-1
    for (int i = 0; i <= n; i++) {
        for (int j = 0; j <= m; j++) {
            if (i < n && j < m && A[i] == B[j]) {
                dp[i + 1][j + 1] = max(dp[i + 1][j + 1], dp[i][j] + 1);
            } else {
                
            }
            if (i < n) {
                dp[i + 1][j] = max(dp[i + 1][j], dp[i][j]);
            }
            if (j < m) {
                dp[i][j + 1] = max(dp[i][j + 1], dp[i][j]);
            }
        }
    }
    
    cout << dp[n][m];
    cout << endl;

    // Walk backwards reconstruct
    vector<int> lcs;
    int i = n;
    int j = m;
    while (i > 0 && j > 0) {
        if (A[i-1] == B[j-1]) {
            lcs.push_back(A[i - 1]);
            i--;
            j--;
            continue;
        }
        if (dp[i][j] == dp[i-1][j]) {
            i--;
            continue;
        }
        j--;
    }
    reverse(lcs.begin(), lcs.end());
    for (auto x : lcs) cout << x << " ";
}