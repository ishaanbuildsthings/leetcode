// n, x = map(int, input().split())
// coins = list(map(int, input().split()))
 
// dp = [-1] * (x + 1) # dp[x] is the minimum number of coins needed to make X, or -1 if not computed
// dp[0] = 0
// for coin in coins:
//   if coin < len(dp) - 1:
//     dp[coin] = 1
 
// for coin in coins:
//   for makeAmount in range(x + 1):
//     if dp[makeAmount] == -1:
//       continue
//     pushed = makeAmount + coin
//     if pushed >= len(dp):
//       break
//     if dp[pushed] == -1:
//       dp[pushed] = 1 + dp[makeAmount]
//     else:
//       dp[pushed] = min(dp[pushed], 1 + dp[makeAmount])
 
// print(dp[-1])
 
#include <bits/stdc++.h>
using namespace std;
 
int main() {
    int n, x;
    cin >> n >> x;
    vector<int> coins(n);
    for (int i = 0; i < n; i++) {
        cin >> coins[i];
    }
 
    vector<int> dp(x + 1, -1);
    dp[0] = 0;
    for (int coin : coins) {
        if (coin < dp.size() - 1) {
            dp[coin] = 1;
        }
    }
 
    for (int coin : coins) {
        for (int makeAmount = 0; makeAmount <= x; makeAmount++) {
            if (dp[makeAmount] == -1) {
                continue;
            }
            int pushed = makeAmount + coin;
            if (pushed >= dp.size()) {
                break;
            }
            if (dp[pushed] == -1) {
                dp[pushed] = 1 + dp[makeAmount];
            } else {
                dp[pushed] = min(dp[pushed], 1 + dp[makeAmount]);
            }
        }
    }
 
    cout << dp[x] << endl;
 
    return 0;
}