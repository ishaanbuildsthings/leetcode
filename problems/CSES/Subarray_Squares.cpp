// Solution 1, dnc dp, O(n * k * log(n))
// #include <bits/stdc++.h>
// using namespace std;
// using ll = long long;

// int main() {
//     cin.tie(nullptr);
//     ios::sync_with_stdio(false);

//     int n, k; cin >> n >> k;
//     vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];

//     vector<vector<ll>> dp(k + 1, vector<ll>(n, -1)); // dp[partitions][i] is the min cost to split that many for 0...i as we loop on i, can optimize to 1d space since we only read previous partitions

//     // seed dp for 1 partition
//     ll tot = 0;
//     for (int i = 0; i < n; i++) {
//         tot += arr[i];
//         dp[1][i] = tot * tot;
//     }

//     ll curr = 0;
//     vector<ll> pf;
//     for (auto x : arr) {
//         curr += x;
//         pf.push_back(curr);
//     }

//     auto cost = [&](int l, int r) -> long long {
//         ll tot = pf[r] - ((l > 0) ? pf[l - 1] : 0);
//         ll sq = tot * tot;
//         return sq;
//     };

//     for (int p = 2; p <= k; p++) {
//         auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
//             if (fillL > fillR) return;
//             int mid = (fillR + fillL) / 2;
//             // brute force scan all left boundaries
//             ll bestTotalCost = LLONG_MAX;
//             int bestJ = -1;
//             for (int j = leftJ; j <= min(rightJ, mid); j++) {
//                 ll costHere = cost(j, mid);
//                 ll prevCost = (j > 0) ? dp[p - 1][j - 1] : 0;
//                 ll totCost = costHere + prevCost;
//                 if (totCost < bestTotalCost) {
//                     bestJ = j;
//                     bestTotalCost = totCost;
//                 }
//             }
//             dp[p][mid] = bestTotalCost;
//             self(self, fillL, mid - 1, leftJ, bestJ);
//             self(self, mid + 1, fillR, bestJ, rightJ);
//         };
//         solve(solve, 0, n - 1, 0, n - 1);
//     }

//     cout << dp[k][n - 1];


// }


// Solution 2, WQS binary search with no optimization, n^2 log(max)
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    cin.tie(nullptr);
    ios::sync_with_stdio(false);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];

    ll tot = 0;
    vector<ll> pf;
    for (auto v : arr) {
        tot += v;
        pf.push_back(tot);
    }

    auto sumQuery = [&](int l, int r) -> ll {
        return pf[r] - ((l > 0) ? pf[l - 1] : 0);
    };

    auto cost = [&](int l, int r) -> ll {
        ll tot = sumQuery(l, r);
        return tot * tot;
    };

    // gives us [min cost, partitions pade]
    auto withCost = [&](ll lambda) -> pair<ll,int> {
        vector<ll> dp(n, LLONG_MAX); // dp[i] is the min cost to split ...i into any number of partitions
        vector<int> bestPartitions(n, -1); // bestPartitions[i] is the best amount of partitions to get the min cost for 0...i
        bestPartitions[0] = 1;

        dp[0] = (1LL * arr[0] * arr[0]) + lambda;
        for (int i = 1; i < n; i++) {
            for (int j = 0; j <= i; j++) {
                // j...i is one group
                ll costSubarray = cost(j, i) + lambda;
                ll prevCost = (j > 0) ? dp[j - 1] : 0;
                ll totCost = costSubarray + prevCost;
                if (totCost < dp[i]) {
                    dp[i] = totCost;
                    bestPartitions[i] = (j > 0) ? (bestPartitions[j - 1] + 1) : 1;
                }
            }
        }

        return {dp[n - 1], bestPartitions[n - 1]};
    };

    // // binary search for a smallest lambda that produces <= k partitions optimally
    ll l = 0;
    ll r = LLONG_MAX / 4;
    ll resLambda = -1;
    ll resCost = -1;
    int resPartitions = -1;
    while (l <= r) {
        ll lambda = l + (r - l) / 2;
        // cerr << "lambda is: " << lambda << endl;
        auto [cost, partitions] = withCost(lambda);
        // cerr << "optimal partitions: " << partitions << endl;
        if (partitions <= k) {
            r = lambda - 1;
            resLambda = lambda;
            resCost = cost;
            resPartitions = partitions;
        } else if (partitions > k) {
            l = lambda + 1;
        }
    }
    ll out = resCost - (resLambda * k);
    cout << out << endl;
}