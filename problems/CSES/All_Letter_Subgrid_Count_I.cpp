// Solution 1, O(n*m*k) but works, O(n*k) memory
// For each cell (r, c) treat it as the bottom right, we need to know the smallest side-length to make a square such that we hit our letter k (for all letters)
// With a small consideration, we allow side-lengths of squares to be stored, that would not fit in the grid (see the code), because it moves a branch out of the hot path
// Solution 2 does this, but it handles one letter at a time, so we need to store n^2 space cause each letter is going to update the penalty in that space
// Instead, we process each row one at a time for all letters first, now the next row only cares about the previous row width * k letters possible space
#include<bits/stdc++.h>
using namespace std;
const int MAX_N = 3000;
const int MAX_K = 26;
const int INF = INT_MAX / 4;
int dp[2][MAX_N][MAX_K]; // dp[column][letter] is the answer for that previous row (space optimized basically)
// the first dimension lets us swap between dp and ndp really quickly
int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;

    // reset array
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < k; j++) {
            dp[0][i][j] = INF;
            dp[1][i][j] = INF;
        }
    }

    long long out = 0;
    for (int r = 0; r < n; r++) {
        string s; cin >> s;
        int OLD = r % 2;
        int NEW = OLD ^ 1;
        for (int c = 0; c < n; c++) {
            int cell = s[c] - 'A';
            int constraint = 0;
            for (int i = 0; i < k; i++) {
                // if we hit this letter we can get away with a side length of 1
                if (cell == i) {
                    dp[NEW][c][i] = 1;
                } else {
                    // if we did not hit this letter and are on a border there is no hope
                    if (r == 0 || c == 0) {
                        dp[NEW][c][i] = INF;
                    } 
                    // look above, left, and up-left to see their dps
                    else {
                        int bottle = dp[OLD][c][i];
                        int x = dp[OLD][c-1][i]; if (x < bottle) bottle = x;
                        x = dp[NEW][c-1][i]; if (x < bottle) bottle = x;
                        if (bottle == INF) {
                            dp[NEW][c][i] = INF;
                        } else {
                            int newSideLength = bottle + 1;
                            dp[NEW][c][i] = newSideLength;
                            // This is brutal, I did this logic to avoid this edge case:
                            // However, that requires this extra branch if/else in a super hot path which caused TLE
                            // Instead, now I just do the line above, dp[NEW][c][i] = newSideLength
                            // It is possible the min sized square at (r, c) is now bigger than the grid actually allows
                            // To fix this, when I add to `out` I claim the gain with 0, moving the logic out of the hot path

                            // it is not sufficient to always set bottle + 1, we actually have to check if we can reach
                            // eg:
                            // B B B
                            // A B B
                            // at the bottom right we might think we can reach A because dp[r][c-1] = 2, but we can't
                            // if (newSideLength > r + 1 || newSideLength > c + 1) {
                            //     dp[NEW][c][i] = INF;
                            // } else {
                            //     dp[NEW][c][i] = newSideLength;
                            // }
                        }
                    }
                }
                constraint = max(constraint, dp[NEW][c][i]);
            }
            // after processing every letter for a cell, we know that smallest possible 
            if (constraint != INF) {
                int gain = min(r + 1, c + 1) - constraint + 1;
                out += max(0, gain);
            }
        }
    }
    cout << out << endl;
}


// Solution 2, O(n*m*k) but TLEs, O(n^2) memory
// For each (r, c) treat it as the bottom right cell
// We need to know the biggest side length here such that we get a letter k (for all k)
// repeat for each letter, now we know the true bottleneck for that cell
// I did best[n][m] which stores the smallest sidelength we can legally use
// also for each letter type I did a rolling dp + ndp
// also note to check the sidelength for (r, c) we use dp[c], dp[c-1], ndp[c-1] as bottlenecks, but that isn't sufficient, we have to check if the square fits:
// it is not sufficient to always set bottle + 1, we actually have to check if we can reach
// eg:
// B B B
// A B B
// at the bottom right we might think we can reach A because dp[r][c-1] = 2, but we can't

// #include <bits/stdc++.h>
// using namespace std;

// const int INF = INT_MAX / 4;
// const int MAX_N = 3000;
// int best[MAX_N][MAX_N]; // best[r][c] is if (r, c) is the bottom right corner of a square, what is smallest side-length we need to be to contain every letter?
// int dp[MAX_N]; // stores best side length, for each letter (one at a time, we overwrite), 1d space optimized to help with time
// int ndp[MAX_N]; // again, the rolling 2 arrays trick
// int grid[MAX_N][MAX_N];
// int main() {
//     ios::sync_with_stdio(false);
//     cin.tie(nullptr);
//     int n, k; cin >> n >> k;
//     // vector<string> grid(n); for (int i = 0; i < n; i++) cin >> grid[i];
//     // for (int i = 0; i < n; i++) cin >> grid[i];
//     char letter;
//     for (int r = 0; r < n; r++) {
//         for (int c = 0; c < n; c++) {
//             cin >> letter;
//             grid[r][c] = letter - 'A';
//         }
//     }


//     // process for each letter separately, what is the best side-length we need to make it so we contain that letter?
//     for (int i = 0; i < k; i++) {
//         for (int r = 0; r < n; r++) {
//             for (int c = 0; c < n; c++) {
//                 if (r == 0 || c == 0) {
//                     if (grid[r][c] == i) {
//                         ndp[c] = 1;
//                     } else {
//                         ndp[c] = INF;
//                     }
//                 } else {
//                     if (grid[r][c] == i) {
//                         ndp[c] = 1;
//                     } else {
//                         int bottle = min(ndp[c-1], min(dp[c], dp[c-1]));
//                         // int bottle = min({ndp[c-1], dp[c], dp[c-1]});
//                         if (bottle == INF) {
//                             ndp[c] = INF;
//                         } else {
//                             // it is not sufficient to always set bottle + 1, we actually have to check if we can reach
//                             // eg:
//                             // B B B
//                             // A B B
//                             // at the bottom right we might think we can reach A because dp[r][c-1] = 2, but we can't
//                             if (bottle <= min(r, c)) {
//                                 ndp[c] = bottle + 1;
//                             } else {
//                                 ndp[c] = INF;
//                             }
//                         }
//                     }
//                 }
//                 best[r][c] = max(best[r][c], ndp[c]);
//             }
//             swap(dp, ndp);
//         }
//     }

//     long long out = 0;
//     for (int r = 0; r < n; r++) {
//         for (int c = 0; c < n; c++) {
//             if (best[r][c] == INF) continue;
//             int bottle = min(r + 1, c + 1);
//             int gained = bottle - best[r][c] + 1;
//             out += gained;
//         }
//     }
//     cout << out << endl;
// }