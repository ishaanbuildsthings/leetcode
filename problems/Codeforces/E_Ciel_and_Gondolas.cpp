// // Solution 1 with dnc dp n*k logn
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// char buf[1 << 22];
// int bufPos = 0, bufLen = 0;

// char readChar() {
//     if (bufPos == bufLen) {
//         bufLen = fread(buf, 1, sizeof(buf), stdin);
//         bufPos = 0;
//     }
//     return buf[bufPos++];
// }

// int readInt() {
//     int x = 0;
//     char c = readChar();
//     while (c < '0' || c > '9') c = readChar();
//     while (c >= '0' && c <= '9') { x = x * 10 + c - '0'; c = readChar(); }
//     return x;
// }

// int main() {
//     int n = readInt(), k = readInt();

//     vector<vector<int>> unfamiliar(n, vector<int>(n));
//     for (int r = 0; r < n; r++) {
//         for (int c = 0; c < n; c++) {
//             unfamiliar[r][c] = readInt();
//         }
//     }

//     vector<vector<int>> pf(n, vector<int>(n)); // pf[r][c] is the sum of 0...c for the r-th person
//     for (int r = 0; r < n; r++) {
//         int tot = 0;
//         for (int c = 0; c < n; c++) {
//             tot += unfamiliar[r][c];
//             pf[r][c] = tot;
//         }
//     }

//     vector<vector<ll>> cost(n, vector<ll>(n, -1)); // cost[l][r] is the precomputed cost
//     for (int l = 0; l < n; l++) {
//         ll totUnfamiliar = 0;
//         for (int r = l; r < n; r++) {
//             int addedSum = pf[r][r];
//             int minus = l > 0 ? pf[r][l - 1] : 0;
//             int totalAdded = addedSum - minus;
//             totUnfamiliar += totalAdded;
//             // adding the r-th person for all l...r people, we need the unfamiliarty sum for that person
//             cost[l][r] = totUnfamiliar;
//         }
//     }

//     vector<int> dp(n, LLONG_MAX / 4LL); // dp[i] is the cost to split 0...i into that many partitions
//     for (int i = 0; i < n; i++) {
//         dp[i] = cost[0][i];
//     }
//     for (int p = 2; p <= k; p++) {
//         vector<int> ndp(n, LLONG_MAX / 4LL);

//         auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
//             if (fillL > fillR) return;
//             int mid = (fillR + fillL) / 2;
//             ll bestCost = LLONG_MAX;
//             int bestJ = -1;
//             for (int j = leftJ; j <= min(rightJ, mid); j++) {
//                 ll costGain = cost[j][mid];
//                 int prevCost = j > 0 ? dp[j - 1] : 0;
//                 ll totCost = costGain + prevCost;
//                 if (totCost < bestCost) {
//                     bestCost = totCost;
//                     bestJ = j;
//                 }
//             }

//             ndp[mid] = bestCost;
//             self(self, fillL, mid - 1, leftJ, bestJ);
//             self(self, mid + 1, fillR, bestJ, rightJ);
//         };

//         solve(solve, 0, n - 1, 0, n - 1);

//         swap(dp, ndp);
//     }

//     cout << dp[n - 1] << '\n';

// }






// Solution 2 with alien trick, n^2 log(max)
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

char buf[1 << 22];
int bufPos = 0, bufLen = 0;

char readChar() {
    if (bufPos == bufLen) {
        bufLen = fread(buf, 1, sizeof(buf), stdin);
        bufPos = 0;
    }
    return buf[bufPos++];
}

int readInt() {
    int x = 0;
    char c = readChar();
    while (c < '0' || c > '9') c = readChar();
    while (c >= '0' && c <= '9') { x = x * 10 + c - '0'; c = readChar(); }
    return x;
}

int main() {
    int n = readInt(), k = readInt();

    vector<vector<int>> unfamiliar(n, vector<int>(n));
    for (int r = 0; r < n; r++) {
        for (int c = 0; c < n; c++) {
            unfamiliar[r][c] = readInt();
        }
    }

    vector<vector<int>> pf(n, vector<int>(n)); // pf[r][c] is the sum of 0...c for the r-th person
    for (int r = 0; r < n; r++) {
        int tot = 0;
        for (int c = 0; c < n; c++) {
            tot += unfamiliar[r][c];
            pf[r][c] = tot;
        }
    }

    vector<vector<int>> cost(n, vector<int>(n, -1)); // cost[l][r] is the precomputed cost
    for (int l = 0; l < n; l++) {
        ll totUnfamiliar = 0;
        for (int r = l; r < n; r++) {
            int addedSum = pf[r][r];
            int minus = l > 0 ? pf[r][l - 1] : 0;
            int totalAdded = addedSum - minus;
            totUnfamiliar += totalAdded;
            // adding the r-th person for all l...r people, we need the unfamiliarty sum for that person
            cost[l][r] = totUnfamiliar;
        }
    }

    vector<ll> dp(n); // answer for ...i, re-used in different penalty calculations
    vector<int> cnt(n); // max (or min, depending on the binary search) partitions to make that dp

    // for a given penalty, tells us the min score and how many divisions we made
    auto withPenalty = [&](ll y) -> pair<ll,int> {
        dp[0] = y;
        cnt[0] = 1;
        for (int r = 1; r < n; r++) {
            ll bestCost = LLONG_MAX / 4LL;
            int bestCount = -1;
            for (int l = 0; l <= r; l++) {
                ll costHere = cost[l][r];
                ll costBefore = l > 0 ? dp[l - 1] : 0;
                int cntBefore = l > 0 ? cnt[l - 1] : 0;
                ll totCost = costHere + costBefore + y;
                // get the most or least count depending on the binary search
                if (totCost < bestCost) {
                    bestCost = totCost;
                    bestCount = cntBefore + 1;
                } else if (totCost == bestCost) {
                    bestCount = min(bestCount, cntBefore + 1);
                }
            }
            dp[r] = bestCost;
            cnt[r] = bestCount;
        }
        return {dp[n - 1], cnt[n - 1]};
    };
    
    ll l = 0;
    ll r = cost[0][n - 1] + 1;
    ll res = -1;
    while (l <= r) {
        ll lambda = l + (r - l) / 2;
        auto [totalSpend, count] = withPenalty(lambda);
        totalSpend -= k * lambda; // important to use k
        // version 1
        // // we are biased to get the most count, so as long as we are >= k we could potentially cross over on a flat segment
        // if (count >= k) {
        //     l = lambda + 1;
        //     res = totalSpend;
        // } else {
        //     r = lambda - 1;
        // }

        // version 2
        // if we are biased to get the least count, so as long as we are <= k we could potentially cross over the flat segment
        if (count <= k) {
            res = totalSpend;
            r = lambda - 1;
        } else {
            l = lambda + 1;
        }
    }

    cout << res << '\n';
    
}