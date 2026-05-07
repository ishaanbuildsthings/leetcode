#include <bits/stdc++.h>
using namespace std;
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    int n, x;
    cin >> n >> x; // num coins, desired sum
 
    vector<int> coins(n);
    for (int i = 0; i < n; i++) {
        cin >> coins[i];
    }
    sort(coins.begin(), coins.end());
 
    vector<int> dp(x + 1, 0); // dp[x] tells us the number of ways to form x
    dp[0] = 1;
    const int MOD = 1e9 + 7;
 
    for (int i = 1; i <= x; i++) {
        int resHere = 0;
        for (int coin : coins) {
            if (i - coin < 0) {
                break;
            }
            resHere = (resHere + dp[i - coin]) % MOD;
        }
        dp[i] = resHere;
    }
 
    cout << dp[x] << "\n";
    return 0;
}