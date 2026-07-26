// #include <bits/stdc++.h>
// using namespace std;
 
// int main() {
//     string strA, strB;
//     getline(cin, strA);
//     getline(cin, strB);
//     // strA = 'LOL'
//     // strB = 'L'
 
//     // print(f"strA={strA}")
//     // print(f"strB={strB}")
 
//     int n = strA.size();
//     int m = strB.size();
 
//     long long INF = 1000000000000000000LL;
//     vector<vector<long long>> dp(n + 1, vector<long long>(m + 1, INF)); // dp[takeA][takeB] is the answer
//     dp[0][0] = 0;
//     for (int i = 0; i <= n; ++i) {
//         dp[i][0] = i;
//     }
//     for (int j = 0; j <= m; ++j) {
//         dp[0][j] = j;
//     }
 
//     // print(dp)
 
//     for (int takeA = 1; takeA <= n; ++takeA) {
//         for (int takeB = 1; takeB <= m; ++takeB) {
//             char a = strA[takeA - 1];
//             char b = strB[takeB - 1];
//             if (a == b) {
//                 dp[takeA][takeB] = dp[takeA - 1][takeB - 1];
//                 continue;
//             }
//             long long resHere = 1 + min({dp[takeA][takeB - 1], dp[takeA - 1][takeB], dp[takeA - 1][takeB - 1]});
//     // resHere = min(resHere, 1 + dp)
//             dp[takeA][takeB] = resHere;
//         }
//     }
 
//     cout << dp[n][m] << '\n';
//     return 0;
// }
 
#include <bits/stdc++.h>
using namespace std;
 
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
 
    string strA, strB;
    getline(cin, strA);
    getline(cin, strB);
    // strA = 'LOL'
    // strB = 'L'
 
    // print(f"strA={strA}")
    // print(f"strB={strB}")
 
    int n = strA.size();
    int m = strB.size();
 
    short INF = 30000;
    vector<vector<short>> dp(n + 1, vector<short>(m + 1, INF)); // dp[takeA][takeB] is the answer
    for (int i = 0; i <= n; ++i) dp[i][0] = i;
    for (int j = 0; j <= m; ++j) dp[0][j] = j;
 
    // print(dp)
 
    function<short(int,int)> calc = [&](int takeA, int takeB) -> short {
        short &memo = dp[takeA][takeB];
        if (memo != INF) return memo;
        char a = strA[takeA - 1];
        char b = strB[takeB - 1];
        if (a == b) {
            memo = calc(takeA - 1, takeB - 1);
            return memo;
        }
        short resHere = static_cast<short>(1 + min({calc(takeA, takeB - 1), calc(takeA - 1, takeB), calc(takeA - 1, takeB - 1)}));
        // resHere = min(resHere, 1 + dp)
        memo = resHere;
        return memo;
    };
 
    cout << calc(n, m) << '\n';
    return 0;
}