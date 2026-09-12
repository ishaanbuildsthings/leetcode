short memo[100001][740];
const short INF = 32000;

class Solution {
public:
    int minDays(int n) {
        

        int maxStreak = (int)sqrt(2.0 * n) + 2;
        for (int i = 0; i <= n; i++) {
            for (int mx = 0; mx <= maxStreak; mx++) {
                memo[i][mx] = -1;
            }
        }

        auto dp = [&](auto&& self, int remain, int prevStreak) -> short {
            if (remain == 0) return 0;

            short& cached = memo[remain][prevStreak];
            if (cached != -1) return cached;

            short res = INF;

            if (prevStreak != 0) {
                short ifReset = 1 + self(self, remain, 0);
                res = ifReset;
            }

            int gain = prevStreak + 1;
            if (gain <= remain) {
                short ifTake = 1 + self(self, remain - gain, prevStreak + 1);
                res = min(res, ifTake);
            }

            cached = res;
            return res;
        };

        return dp(dp, n, 0);
    }
};