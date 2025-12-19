#include <bits/stdc++.h>
using namespace std;

int sequenceLength, maxDigit;
const long long MOD = 998244353;

long long memo[1001][12][12][12];

long long dp(int i, int min1, int min2, int min3) {
    long long &ans = memo[i][min1][min2][min3];
    if (ans != -1) return ans;
    if (i == sequenceLength) return ans = (min3 != 11);
    long long resHere = 0;
    for (int nextDigit = 1; nextDigit <= maxDigit; ++nextDigit) {
        if (nextDigit > min3) break;
        int newMin1 = min(min1, nextDigit);
        int newMin2 = min2;
        if (nextDigit > min1) newMin2 = min(newMin2, nextDigit);
        int newMin3 = min3;
        if (nextDigit > min2) newMin3 = min(newMin3, nextDigit);
        resHere += dp(i + 1, newMin1, newMin2, newMin3);
        if (resHere >= MOD) resHere -= MOD;
    }
    return ans = resHere;
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    cin >> sequenceLength >> maxDigit;
    memset(memo, -1, sizeof(memo));
    cout << dp(0, 11, 11, 11) % MOD << '\n';
    return 0;
}

// Commented out because python was too slow
// import sys

// sequenceLength, maxDigit = map(int, sys.stdin.readline().split())

// MOD = 998244353

// from functools import lru_cache

// @lru_cache(maxsize=None)
// def dp(i, min1, min2, min3):
//   if i == sequenceLength:
//     return 1 if min3 != 11 else 0
//   resHere = 0
//   for nextDigit in range(1, maxDigit + 1):
//     if nextDigit > min3:
//       break
//     newMin1 = min(min1, nextDigit)
//     newMin2 = min2
//     if nextDigit > min1:
//       newMin2 = min(newMin2, nextDigit)
//     newMin3 = min3
//     if nextDigit > min2:
//       newMin3 = min(newMin3, nextDigit)
//     resHere += dp(i + 1, newMin1, newMin2, newMin3)
//   return resHere % MOD

// print(dp(0,11,11,11))
