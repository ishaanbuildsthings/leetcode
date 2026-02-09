class Solution {
    public:
        int zigZagArrays(int n, int l, int r) {
            int MOD = 1000000000 + 7;
            vector<vector<int>> dp(r + 1, vector<int>(2, 0)); // dp[prev][prevUp]
            for (int v = l; v <= r; v++) {
                dp[v][0] = 1;
                dp[v][1] = 1;
            }
    
            vector<vector<int>> ndp(r + 1, vector<int>(2, 0));
            vector<int> pfPrevUp(r + 1, 0);
            vector<int> pfPrevDown(r + 1, 0);
    
            for (int number = 2; number <= n; number++) {
                // reset ndp
                for (int v = l; v <= r; v++) {
                    ndp[v][0] = 0;
                    ndp[v][1] = 0;
                }
                // reset pf
                int currUp = 0;
                int currDown = 0;
                for (int prevVal = l; prevVal <= r; prevVal++) {
                    currUp += dp[prevVal][1];
                    currUp %= MOD;
                    currDown += dp[prevVal][0];
                    currDown %= MOD;
                    pfPrevUp[prevVal] = currUp;
                    pfPrevDown[prevVal] = currDown;
                }
    
    
                for (int newVal = l; newVal <= r; newVal++) {
                    // handle prev went up
                    if (newVal + 1 <= r) {
                        int score = (pfPrevUp[r] - ((newVal + 1) > 0 ? pfPrevUp[newVal] : 0)) % MOD;
                        if (score < 0) score += MOD;
                        ndp[newVal][0] = score;
                    }
                    // handle prev went down
                    if (l <= newVal - 1) {
                        int score = (pfPrevDown[newVal - 1] - (l > 0 ? pfPrevDown[l - 1] : 0)) % MOD;
                        if (score < 0) score += MOD;
                        ndp[newVal][1] = score;
                    }
                }
    
                dp.swap(ndp);
            }
    
            int ans = 0;
            for (int v = l; v <= r; v++) {
                ans += dp[v][0];
                ans %= MOD;
                ans += dp[v][1];
                ans %= MOD;
            }
            return ans;
        }
    };