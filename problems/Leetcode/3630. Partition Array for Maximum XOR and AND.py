class Solution {
public:
    long long maximizeXorAndXor(vector<int>& nums) {
        int n = nums.size();
        long long res = 0;

        int fmask = (1 << n) - 1;

        vector<int> memo(fmask + 1, -1);
        auto andOf = [&](auto& self, int mask) -> int {
            if (mask == 0) {
                return 0;
            }
            if (memo[mask] != -1) {
                return memo[mask];
            }
            int msb = 31 - __builtin_clz(mask);
            int rest = mask ^ (1 << msb);
            if (rest == 0) {
                return memo[mask] = nums[msb];
            }
            return memo[mask] = nums[msb] & self(self, rest);
        };

        auto maxXorSubset = [&](int* arr, int cnt) -> int {
            int slots[30] = {};
            for (int i = 0; i < cnt; i++) {
                int v = arr[i];
                while (v) {
                    int msb = 31 - __builtin_clz(v);
                    if (!slots[msb]) {
                        slots[msb] = v;
                        break;
                    } else {
                        v ^= slots[msb];
                    }
                }
            }
            int res = 0;
            for (int b = 29; b >= 0; b--) {
                if (!slots[b]) {
                    continue;
                }
                if (!(res & (1 << b))) {
                    res ^= slots[b];
                }
            }
            return res;
        };

        int forXors[19];
        int removedOddBits[19];

        for (int inAndMask = 0; inAndMask <= fmask; inAndMask++) {
            int andVals = andOf(andOf, inAndMask);
            int cnt = 0;
            for (int b = 0; b < n; b++) {
                if (!(inAndMask & (1 << b))) {
                    forXors[cnt++] = nums[b];
                }
            }

            int sumXors = 0;
            for (int i = 0; i < cnt; i++) {
                sumXors ^= forXors[i];
            }

            for (int i = 0; i < cnt; i++) {
                removedOddBits[i] = forXors[i] & ~sumXors;
            }

            int maxXor = maxXorSubset(removedOddBits, cnt);

            res = max(res, (long long)andVals + 2LL * maxXor + sumXors);
        }

        return res;
    }
};