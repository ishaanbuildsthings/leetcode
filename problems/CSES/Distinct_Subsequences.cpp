// SOLUTION 1, 26N dp
// at a position, we can chain to all of the next letters that occur, at their first positions
// really we can just optimize this to 1N dp by taking the suffix sum for every unique letter type, or something like that, similar to solution 2, i think this reduces to that
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// const int MOD = 1000000007;

// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     string s; cin >> s;
//     s = '#' + s;
//     int n = s.size();

//     string ABC = "abcdefghijklmnopqrstuvwxyz";
    
//     vector<vector<int>> cache(n, vector<int>(26, -1));
//     // finds first occurrence of a letter in i..., or -1 if it does not exist
//     auto first = [&](auto&& self, int i, int charI) -> int {
//         if (i == n) return -1;
//         char c = ABC[charI];
//         if (s[i] == c) return i;
//         auto& res = cache[i][charI];
//         if (res != -1) return res;
//         res = self(self, i + 1, charI);
//         return res;
//     };

//     vector<int> cache2(n, -1);
//     // tells us how many sequences we get if we must include this index
//     auto dp = [&](auto&& self, int i) -> int {
//         if (i == n) return 0;
//         if (i == n - 1) return 1;
//         if (cache2[i] != -1) return cache2[i];
//         int res = 1; // end here
//         for (int j = 0; j < 26; j++) {
//             int nextI = first(first, i + 1, j);
//             if (nextI != -1) {
//                 res += self(self, nextI);
//                 res %= MOD;
//             }
//         }
//         cache2[i] = res;
//         return res;
//     };

//     int ans = dp(dp, 0);
//     ans--;
//     if (ans < 0) ans += MOD;
//     cout << ans;
// }




// SOLUTION 2, O(1 * N) dp
// dp[i] is the # of subsequences in ...i
// at a new i we can add this letter to all previous subsequences
// but we must subtract endingAt[currentLetter] to avoid duplicates
#include <bits/stdc++.h>
using namespace std;
using ll = long long;
const int MOD = 1000000007;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    vector<int> endingAt(26, 0);
    int totalSequences = 1; // empty subsequence
    for (int i = 0; i < s.size(); i++) {
        char c = s[i];
        int charI = c - 'a';
        int newTotal = (2 * totalSequences) % MOD; // we can append this letter to any previous subsequence
        newTotal -= endingAt[charI]; // but any previous sequence made, ending in this letter, gets double counted
        if (newTotal < 0) newTotal += MOD;
        endingAt[charI] = totalSequences;
        totalSequences = newTotal;
    }
    cout << (totalSequences - 1 + MOD) % MOD; // subtract empty sequence
}