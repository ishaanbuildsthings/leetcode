#include<bits/stdc++.h>
using namespace std;
int MOD = 1000000000 + 7;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n; cin >> n;
    vector<int> A(n);
    for (int i = 0; i < n; i++) cin >> A[i];

    vector<int> dp(n + 1); // dp[i] is the answer for i...
    dp[n] = 1; // base case
    vector<int> suff(n + 1); // suff[i] is dp[i] + dp[i + 1] + ...
    suff[n] = 1;

    // For each left index, need to see how far right we can go
    int r = 0;
    vector<int> rights(n + 1);
    unordered_map<int, int> frq;

    for (int l = 0; l < n; l++) {
        while (r < n && frq[A[r]] == 0) {
            frq[A[r]]++;
            r++;
        }
        rights[l] = r - 1;
        frq[A[l]]--;
    }

    // 0 1 2 |3| 4 5 6 7| 8 9 10 11 12
    // 3 can go to 7 distinct
    // so we range add 4-8
    for (int i = n - 1; i >= 0; i--) {
        int rightmost = rights[i];
        int r = rightmost + 1;
        int l = i + 1;
        int leftContribution = suff[l];
        int lostRight = r + 1 <= n ? suff[r + 1] : 0;
        int gained = (leftContribution - lostRight);
        if (gained < 0) gained += MOD;
        dp[i] = gained;
        suff[i] = (dp[i] + suff[i + 1]) % MOD;
    }

    cout << dp[0];
}