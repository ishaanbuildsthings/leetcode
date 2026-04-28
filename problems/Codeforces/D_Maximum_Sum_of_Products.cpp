#include<bits/stdc++.h>
using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n); for (int i = 0; i < n; i++) cin >> A[i];
    vector<int> B(n); for (int i = 0; i < n; i++) cin >> B[i];
    vector<vector<long long>> dp(n, vector<long long>(n, 0));
    for (int i = 0; i < n; i++) {
        dp[i][i] = (long long)A[i] * B[i];
    }
    for (int sz = 2; sz <= n; sz++) {
        for (int l = 0; l < n; l++) {
            int r = l + sz - 1;
            if (r >= n) break;
            long long inner = (l + 1 == r) ? 0 : dp[l + 1][r - 1];
            long long gain = (long long)A[l] * B[r] + (long long)A[r] * B[l];
            dp[l][r] = gain + inner;
        }
    }
    vector<long long> pf(n);
    long long curr = 0;
    for (int i = 0; i < n; i++) {
        curr += (long long)A[i] * B[i];
        pf[i] = curr;
    }
    vector<long long> suff(n);
    curr = 0;
    for (int i = n - 1; i >= 0; i--) {
        curr += (long long)A[i] * B[i];
        suff[i] = curr;
    }
    long long out = 0;
    for (int l = 0; l < n; l++) {
        for (int r = l; r < n; r++) {
            long long left = l > 0 ? pf[l - 1] : 0;
            long long right = r < n - 1 ? suff[r + 1] : 0;
            long long inside = dp[l][r];
            long long tot = left + right + inside;
            out = max(out, tot);
        }
    }
    cout << out << endl;
}