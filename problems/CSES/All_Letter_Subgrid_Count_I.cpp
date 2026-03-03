#include <bits/stdc++.h>
using namespace std;


// using ll = long long;
const int INF = INT_MAX / 4;
const int MAX_N = 3000;
int best[MAX_N][MAX_N]; // best[r][c] is if (r, c) is the bottom right corner of a square, what is smallest side-length we need to be to contain every letter?
int dp[MAX_N]; // stores best side length, for each letter (one at a time, we overwrite), 1d space optimized to help with time
int ndp[MAX_N]; // again, the rolling 2 arrays trick
string grid[MAX_N];
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    // vector<string> grid(n); for (int i = 0; i < n; i++) cin >> grid[i];
    for (int i = 0; i < n; i++) cin >> grid[i];


    // process for each letter separately, what is the best side-length we need to make it so we contain that letter?
    for (int i = 0; i < k; i++) {
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                if (r == 0 || c == 0) {
                    if (grid[r][c] - 'A' == i) {
                        ndp[c] = 1;
                    } else {
                        ndp[c] = INF;
                    }
                } else {
                    if (grid[r][c] - 'A' == i) {
                        ndp[c] = 1;
                    } else {
                        int bottle = min({ndp[c-1], dp[c], dp[c-1]});
                        if (bottle == INF) {
                            ndp[c] = INF;
                        } else {
                            // it is not sufficient to always set bottle + 1, we actually have to check if we can reach
                            // eg:
                            // B B B
                            // A B B
                            // at the bottom right we might think we can reach A because dp[r][c-1] = 2, but we can't
                            if (bottle <= min(r, c)) {
                                ndp[c] = bottle + 1;
                            } else {
                                ndp[c] = INF;
                            }
                        }
                    }
                }
                best[r][c] = max(best[r][c], ndp[c]);
            }
            swap(dp, ndp);
        }
    }

    long long out = 0;
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            if (best[r][c] == INF) continue;
            int bottle = min(r + 1, c + 1);
            int gained = bottle - best[r][c] + 1;
            out += gained;
            // cout << "gained: " << gained << "for r= " << r << " c=" << c << endl;
        }
    }
    cout << out << endl;

    // for (auto& row : best) {
    //     for (auto v : row) {
    //         cout << v << " ";
    //     }
    //     cout << endl;
    // }
}