int dp[5001][5001][2];   
class Solution {
public:
    int minOperations(vector<int>& nums, int k) {
        int n = nums.size();

        auto score = [&](int i) -> int {
            int l = (i > 0) ? nums[i - 1] : nums[n - 1];
            int r = (i < n - 1) ? nums[i + 1] : nums[0];
            int mx = max(l, r);
            int req = mx + 1;
            if (nums[i] >= req) return 0;
            return req - nums[i];
        };

        vector<int> scores(n);
        for (int i = 0; i < n; i++) scores[i] = score(i);

        
        for (int i = 0; i <= n; i++) {
            for (int ki = 0; ki <= k; ki++) {
                dp[i][ki][0] = -1;
                dp[i][ki][1] = -1;
            }
        }

        int INF = 1000000000;

        auto fn = [&](auto&& self, int i, int peaksLeft, int takeFirst) -> int {
            if (peaksLeft == 0) {
                return 0;
            }
            // cant take last, fail immediately
            if (i == n - 1 && takeFirst) {
                return INF;
            }
            // no options
            if (i >= n) {
                return INF;
            }
            // in memo
            if (dp[i][peaksLeft][takeFirst] != -1) {
                return dp[i][peaksLeft][takeFirst];
            }
            int ifCont = self(self, i + 1, peaksLeft, takeFirst);
            int tf = 0;
            if (i == 0) tf = 1;
            int take = scores[i] + self(self, i + 2, peaksLeft - 1, takeFirst || tf);
            int res = min(take, ifCont);
            dp[i][peaksLeft][takeFirst] = res;
            return res;
        };

        int answer = fn(fn,0,k,0);
        if (answer == INF) return -1;
        return answer;
    }
};