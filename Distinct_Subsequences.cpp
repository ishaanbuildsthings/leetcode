#include <bits/stdc++.h>
using namespace std;
using ll = long long;

const int MOD = 1000000007;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    string s; cin >> s;
    s = '#' + s;
    int n = s.size();

    string ABC = "abcdefghijklmnopqrstuvwxyz";
    
    vector<vector<int>> cache(n, vector<int>(26, -1));
    // finds first occurrence of a letter in i..., or -1 if it does not exist
    auto first = [&](auto&& self, int i, int charI) -> int {
        if (i == n) return -1;
        char c = ABC[charI];
        if (s[i] == c) return i;
        auto& res = cache[i][charI];
        if (res != -1) return res;
        res = self(self, i + 1, charI);
        return res;
    };

    vector<int> cache2(n, -1);
    // tells us how many sequences we get if we must include this index
    auto dp = [&](auto&& self, int i) -> int {
        if (i == n) return 0;
        if (i == n - 1) return 1;
        if (cache2[i] != -1) return cache2[i];
        int res = 1; // end here
        for (int j = 0; j < 26; j++) {
            int nextI = first(first, i + 1, j);
            if (nextI != -1) {
                res += self(self, nextI);
                res %= MOD;
            }
        }
        cache2[i] = res;
        return res;
    };

    int ans = dp(dp, 0);
    ans--;
    if (ans < 0) ans += MOD;
    cout << ans;
}