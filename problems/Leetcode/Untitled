const int MAX_UNIQ = 2000;
const int MAX_XOR  = 2048;
int cache[MAX_UNIQ][MAX_XOR][2];
const int INF = INT_MAX / 4;

class Solution {
public:
    int minOperations(vector<int>& nums) {
        int n = nums.size();

        int maxValue = 0;
        for (int value : nums) maxValue = max(maxValue, value);

        int xorLimit = 1;
        while (xorLimit <= maxValue) xorLimit <<= 1;

        set<int> uniqSet(nums.begin(), nums.end());
        vector<int> uniq(uniqSet.begin(), uniqSet.end());

        int uniqCount = uniq.size();

        if (uniqCount == 1) return (n % 2) ? -1 : 0;

        int xorAll = 0;
        for (int value : nums) xorAll ^= value;

        for (int i = 0; i < uniqCount; i++) {
            for (int x = 0; x < xorLimit; x++) {
                cache[i][x][0] = -1;
                cache[i][x][1] = -1;
            }
        }

        auto dp = [&](auto&& self, int i, int prevXor, int skippedAny) -> int {
            if (i == uniqCount) return (prevXor == 0 && skippedAny) ? 0 : INF;

            int &memo = cache[i][prevXor][skippedAny];
            if (memo != -1) return memo;

            int ifSkip = self(self, i + 1, prevXor, 1);
            int ifTake = 1 + self(self, i + 1, prevXor ^ uniq[i], skippedAny);

            memo = min(ifSkip, ifTake);
            return memo;
        };

        int ans = dp(dp, 0, xorAll, uniqCount == n ? 0 : 1);
        return ans < INF ? ans : -1;
    }
};