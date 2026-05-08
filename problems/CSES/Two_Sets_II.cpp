// n = int(input())
// MOD = 10**9 + 7
 
// from functools import lru_cache
 
// @lru_cache(maxsize=None)
// def dp(num, topSurplus):
//   if num == n + 1:
//     return int(topSurplus == 0)
//   ifTop = dp(num + 1, topSurplus + num)
//   ifBot = dp(num + 1, abs(topSurplus - num))
//   return (ifTop + ifBot) % MOD
// total_sum = n * (n + 1) // 2
// if total_sum % 2:
//     print(0)
// else:
//   print((dp(1, 0) * pow(2, MOD-2, MOD)) % MOD)
 
#include <bits/stdc++.h>
using namespace std;
 
int n;
int MOD = 1000000007;
vector<vector<long long>> memo;
 
long long dp(int num, int topSurplus) {
    if (num == n + 1) {
        return (topSurplus == 0) ? 1 : 0;
    }
    if (memo[num][topSurplus] != -1) {
        return memo[num][topSurplus];
    }
    long long ifTop = dp(num + 1, topSurplus + num);
    long long ifBot = dp(num + 1, abs(topSurplus - num));
    return memo[num][topSurplus] = (ifTop + ifBot) % MOD;
}
 
int main() {
    cin >> n;
    int total_sum = n * (n + 1) / 2;
    memo.assign(n + 1, vector<long long>(total_sum + 1, -1));
 
    if (total_sum % 2) {
        cout << 0 << endl;
    } else {
        cout << (dp(1, 0) * 500000004LL) % MOD << endl;
    }
    return 0;
}