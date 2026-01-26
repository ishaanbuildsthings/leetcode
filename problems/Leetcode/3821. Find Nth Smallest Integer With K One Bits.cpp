class Solution {
    public:
        long long nthSmallest(long long n, int k) {
            long long l = 1; // all 1s
            for (int i = 0; i < k - 1; i++) {
                l <<= 1;
                l += 1;
            }
            // how many numbers have k one bits <= x
            auto lte = [&](long long x) -> long long {
                string s;
                while (x) {
                    int bit = x & 1;
                    if (bit) {
                        s.push_back('1');
                    } else {
                        s.push_back('0');
                    }
                    x >>= 1;
                }
                reverse(s.begin(), s.end());
    
                vector<vector<long long>> cache(s.size(), vector<long long>(k + 1, -1)); // cache[i][oneBits] -> answer for no tight
                auto dp = [&](auto&& self, int i, int oneBits, int tight) -> long long {
                    if (oneBits > k) return 0;
                    if (i == s.size()) {
                        return oneBits == k ? 1 : 0;
                    }
                    if (!tight && cache[i][oneBits] != -1) {
                        return cache[i][oneBits];
                    }
                    char c = s[i];
                    int upper = -1;
                    if (!tight) {
                        upper = 1;
                    } else {
                        if (c == '0') {
                            upper = 0;
                        } else {
                            upper = 1;
                        }
                    }
                    long long resHere = 0;
                    for (int nxt = 0; nxt <= upper; nxt++) {
                        int ntight = -1;
                        if (tight && nxt == upper) {
                            ntight = 1;
                        } else {
                            ntight = 0;
                        }
                        int nones = oneBits + nxt;
                        resHere += self(self, i + 1, nones, ntight);
                    }
                    if (!tight) {
                        cache[i][oneBits] = resHere;
                    }
                    return resHere;
                };
    
                return dp(dp, 0, 0, 1);
            };
    
            long long r = 1LL << 50;
            long long res = -1;
            while (l <= r) {
                long long m = l + (r - l) / 2;
                if (lte(m) >= n) {
                    res = m;
                    r = m - 1;
                } else {
                    l = m + 1;
                }
            }
            return res;
        }
    };