#include <bits/stdc++.h>
using namespace std;
using ll = long long;

class Solution {
public:
    long long minimumCost(vector<int>& nums, vector<int>& cost, int k) {
        int n = nums.size();
        
        vector<ll> pfN(n), pfC(n);
        ll curr = 0;
        for (int i = 0; i < n; i++) {
            curr += nums[i];
            pfN[i] = curr;
        }
        curr = 0;
        for (int i = 0; i < n; i++) {
            curr += cost[i];
            pfC[i] = curr;
        }
        
        auto subQuery = [&](int l, int r, int i) -> ll {
            ll costSum = pfC[r] - (l > 0 ? pfC[l - 1] : 0);
            return costSum * (pfN[r] + (ll)k * i);
        };
        
        vector<vector<ll>> dp(n, vector<ll>(n + 1, LLONG_MAX));
        
        for (int i = 0; i < n; i++)
            dp[i][1] = subQuery(0, i, 1);
        
        for (int p = 2; p <= n; p++) {
            auto solve = [&](auto& self, int fillL, int fillR, int leftJ, int rightJ) -> void {
                if (fillL > fillR) return;
                int mid = (fillL + fillR) / 2;
                
                ll bestHere = LLONG_MAX;
                int bestJ = leftJ;
                
                for (int j = leftJ; j <= min(mid, rightJ); j++) {
                    ll costPortion = subQuery(j, mid, p);
                    ll prevAns = j > 0 ? dp[j - 1][p - 1] : 0;
                    ll totCost = costPortion + prevAns;
                    if (totCost < bestHere) {
                        bestHere = totCost;
                        bestJ = j;
                    }
                }
                
                dp[mid][p] = bestHere;
                self(self, fillL, mid - 1, leftJ, bestJ);
                self(self, mid + 1, fillR, bestJ, rightJ);
            };
            
            solve(solve, 0, n - 1, 0, n - 1);
        }
        
        ll ans = LLONG_MAX;
        for (int p = 1; p <= n; p++)
            ans = min(ans, dp[n - 1][p]);
        
        return ans;
    }
};