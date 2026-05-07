
 
// for coinType in coins:
//   for makeThisAmount in range(targetSum + 1):
//     prev = makeThisAmount - coinType
//     if prev < 0:
//       continue
//     prevWays = dp[prev]
//     dp[makeThisAmount] += prevWays
//     if dp[makeThisAmount] >= MOD:
//       dp[makeThisAmount] -= MOD
 
// print(dp[-1])
 
#include <iostream>
#include <vector>
using namespace std;
 
int main() {
    int numCoins, targetSum;
    cin >> numCoins >> targetSum;
 
    vector<int> coins(numCoins);
    for (int i = 0; i < numCoins; i++) {
        cin >> coins[i];
    }
 
    vector<int> dp(targetSum + 1, 0);
    dp[0] = 1;
 
    int MOD = 1000000007;
 
    for (int coinType : coins) {
        for (int makeThisAmount = 0; makeThisAmount <= targetSum; makeThisAmount++) {
            int prev = makeThisAmount - coinType;
            if (prev < 0) {
                continue;
            }
            int prevWays = dp[prev];
            dp[makeThisAmount] += prevWays;
            if (dp[makeThisAmount] >= MOD) {
                dp[makeThisAmount] -= MOD;
            }
        }
    }
 
    cout << dp[targetSum] << endl;
 
    return 0;
}
