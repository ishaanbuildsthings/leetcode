#include <bits/stdc++.h>
using namespace std;
using ll = long long;
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<string> grid(n); for (int i = 0; i < n; i++) cin >> grid[i];
    vector<ll> out(k);
    vector<vector<int>> dp(n, vector<int>(n, 0)); // dp[r][c] is the largest square we can make with (r, c) as the bottom right corner
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            char chr = grid[r][c];
            if (r > 0 && c > 0 && grid[r-1][c] == chr && grid[r-1][c-1] == chr && grid[r][c-1] == chr) {
                int bottle = min({dp[r-1][c], dp[r][c-1], dp[r-1][c-1]});
                int res = bottle + 1;
                out[chr - 'A'] += res;
                dp[r][c] = res;
            } else {
                out[chr - 'A']++;
                dp[r][c] = 1;
            }
        }
    }
    for (auto x : out) cout << x << '\n';
}