// MAX sparse table
// O(n log n) build
// O(1) range MAX
struct SparseMax {
    int n, LOG;
    vector<vector<long long>> sparse;
    SparseMax(const vector<long long>& arr) {
        n = (int)arr.size();
        LOG = (n == 0) ? 1 : (32 - __builtin_clz(n));
        sparse.assign(LOG, vector<long long>(n, 0));
        for (int i = 0; i < n; i++)
            sparse[0][i] = arr[i];
        for (int power = 1; power < LOG; power++) {
            int halfWidth = 1 << (power - 1);
            for (int left = 0; left < n; left++) {
                long long val = sparse[power - 1][left];
                int rightEdge = left + halfWidth;
                if (rightEdge < n)
                    val = max(val, sparse[power - 1][rightEdge]);
                sparse[power][left] = val;
            }
        }
    }
    long long query(int l, int r) {
        int width = r - l + 1;
        int maxPow = 31 - __builtin_clz(width);
        int powWidth = 1 << maxPow;
        return max(
            sparse[maxPow][l],
            sparse[maxPow][l + width - powWidth]
        );
    }
};

class Solution {
public:
    long long maximumSum(vector<int>& nums, int m, int l, int r) {
        const long long INF = (long long)4e18;
        int n = (int)nums.size();

        vector<long long> pf;
        long long curr = 0;
        for (int v : nums) {
            curr += v;
            pf.push_back(curr);
        }

        auto query = [&](int L, int R) -> long long {
            if (L >= n)
                return 0;
            return pf[R] - (L ? pf[L - 1] : 0);
        };

        vector<vector<long long>> dp(n, vector<long long>(m + 1, -INF));
        // dp[i][p] is the max score to partition 0...i into exactly p subarrays
        for (int i = 0; i < n; i++)
            dp[i][0] = 0;

        for (int p = 1; p <= m; p++) {
            vector<long long> previousDp;
            for (int i = 0; i < n; i++)
                previousDp.push_back(dp[i][p - 1]);
            vector<long long> forSparseTable;
            long long pfMax = 0;
            for (int i = 0; i < n; i++) {
                long long suffTot = query(i, n - 1);
                forSparseTable.push_back(pfMax + suffTot);
                pfMax = max(pfMax, previousDp[i]);
            }
            SparseMax st(forSparseTable);

            // iterate over the right edge of the subarray
            for (int right = 0; right < n; right++) {
                // the leftmost and rightmost possible points we can select for the left edge
                int LEFT = right - r + 1;
                int RIGHT = right - l + 1;
                if (RIGHT < 0) {
                    dp[right][p] = -INF;
                    continue;
                }
                LEFT = max(LEFT, 0);
                // we want the max dp from LEFT...RIGHT
                // our optimal left edge lives somewhere in here
                // we can "test" every left edge with a range query, it's a bit tricky
                // we need to get a prefixMaxDp[i] which is the answer for the previous partition count
                // for any subarray ending up to i, but not necessarily at i, thats why its a prefix max
                // and we include the suffix sum inside it to help keep things independent
                long long previousPrefixMaxPlusSuffixSum = st.query(LEFT, RIGHT);
                long long subtractedSum = query(right + 1, n - 1);
                long long newAnswer = previousPrefixMaxPlusSuffixSum - subtractedSum;
                dp[right][p] = newAnswer;
            }
        }

        long long res = -INF;
        for (int p = 1; p <= m; p++)
            for (int i = 0; i < n; i++)
                res = max(res, dp[i][p]);
        return res;
    }
};