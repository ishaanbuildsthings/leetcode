#include <bits/stdc++.h>
using namespace std;
using ll = long long;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);
    int n, k; cin >> n >> k;
    vector<int> arr(n); for (int i = 0; i < n; i++) cin >> arr[i];
    vector<vector<ll>> cost(n, vector<ll>(n, 0)); // optimal cost for l...r if we can place the school anywhere in that range
    for (int l = 0; l < n; l++) {
        int m = l;
        ll leftWeight = arr[l]; // weight of elements at or left of median (including median)
        ll rightWeight = 0;
        ll curCost = 0;
        cost[l][l] = 0;
    
        for (int r = l + 1; r < n; r++) {
            // arr[r] joins the right side, at distance (r - m) from school
            curCost += (ll)arr[r] * (r - m); // current cost to get to median
            rightWeight += arr[r];
    
            // shift median right while right side is heavier
            while (m < r && leftWeight < rightWeight) {
                curCost += leftWeight - rightWeight;
                m++;
                leftWeight += arr[m];
                rightWeight -= arr[m];
            }
    
            cost[l][r] = curCost;
        }
    }

    vector<ll> dp(n, LLONG_MAX); // min cost to partition 0...i as we loop on partitions
    vector<ll> ndp(n, LLONG_MAX);
    // seed for 1 partition
    for (int i = 0; i < n; i++) {
        dp[i] = cost[0][i];
    }

    for (int p = 2; p <= k; p++) {
        auto solve = [&](auto&& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
            if (fillL > fillR) return;
            int mid = (fillR + fillL) / 2;
            ll best = LLONG_MAX;
            int bestJ = -1;
            for (int j = leftJ; j <= min(mid, rightJ); j++) {
                ll costThisGroup = cost[j][mid];
                ll costBefore = j > 0 ? dp[j - 1] : 0;
                ll totCost = costThisGroup + costBefore;
                if (totCost < best) {
                    best = totCost;
                    bestJ = j;
                }
            }
            ndp[mid] = best;
            self(self, fillL, mid - 1, leftJ, bestJ);
            self(self, mid + 1, fillR, bestJ, rightJ);
        };
        solve(solve, 0, n - 1, 0, n - 1);
        swap(dp, ndp);
    }
    cout << dp[n - 1] << endl;
}