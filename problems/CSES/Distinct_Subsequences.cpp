#include<bits/stdc++.h>
using namespace std;
int MOD = 1000000000 + 7;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    int n = s.size();
    int SENTINEL = n + 1;
    vector<int> earliest(26, SENTINEL);
    vector<vector<int>> nxt(n, vector<int>(26));
    for (int i = n - 1; i >= 0; i--) {
        for (int letter = 0; letter < 26; letter++) {
            nxt[i][letter] = earliest[letter];
        }
        char c = s[i];
        earliest[c - 'a'] = i;
    }
    vector<int>dp(n); // dp[i] is the number of subsequences in s[i:] where we must use the i-th letterc
    for (int i = n - 1; i >= 0; i--) {
        int ways = 1; // can just use this single letter.
        for (int nextLetter = 0; nextLetter < 26; nextLetter++) {
            if (nxt[i][nextLetter] == SENTINEL) {
                continue;
            }
            ways += dp[nxt[i][nextLetter]];
            ways %= MOD;
        }
        dp[i] = ways;
    }
    int result = 0;
    for (auto c : "abcdefghijklmnopqrstuvwxyz") {
        for (int i = 0; i < n; i++) {
            if (s[i] == c) {
                result += dp[i];
                result %= MOD;
                break;
            }
        }
    }
    cout << result;
}