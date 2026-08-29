// TEMPLATE BY ISHAANBUILDSTHINGS on github
// Construct a GCD sparse table
// O(n log n log(maxVal)) build time
// O(log(maxVal)) query range GCD, so effectively O(1)
// ⚠️ Not optimized, also my style is a bit weird as I populate sparse[power][left] even when it would go past the right edge, might be slower to build
#include <bits/stdc++.h>
using namespace std;
struct Sparse {
    int n;
    int LOG;
    vector<vector<int>> sparse; // sparse[power][left] is the GCD for that range
    Sparse(const vector<int>& arr) {
        n = arr.size();
        LOG = 32 - __builtin_clz(n);
        sparse.resize(LOG, vector<int>(n));
        for (int i = 0; i < n; i++) {
            sparse[0][i] = arr[i];
        }
        for (int power = 1; power < LOG; power++) {
            int width = 1 << power;
            int halfWidth = width / 2;
            for (int left = 0; left < n; left++) {
                int gcdLeft = sparse[power-1][left];
                int rightEdge = left + halfWidth;
                if (rightEdge < n) {
                    gcdLeft = gcd(gcdLeft, sparse[power-1][rightEdge]);
                }
                sparse[power][left] = gcdLeft;
            }
        }
    }
    int query(int l, int r) {
        int width = r - l + 1;
        int maxPow = 31 - __builtin_clz(width);
        int powWidth = 1 << maxPow;
        int left = sparse[maxPow][l];
        int right = sparse[maxPow][l + width - powWidth];
        return gcd(left, right);
    }
};

class Solution {
public:
    int maxValidSplits(vector<int>& nums) {
        int n = nums.size();
        Sparse st(nums);

        auto queryGcd = [&](int l, int r, int brokenI) {
            if (brokenI < l || brokenI > r) {
                return st.query(l, r);
            }
            if (brokenI == l) {
                return st.query(l + 1, r);
            }
            if (brokenI == r) {
                return st.query(l, r - 1);
            }
            int lh = st.query(l, brokenI - 1);
            int rh = st.query(brokenI + 1, r);
            return gcd(lh, rh);
        };

        int res = 0;
        for (int i = 0; i < n; i++) {
            // binary search leftmost position the prefix gcd equals the suffix
            int L = (i != 0) ? 0 : 1;
            int R = (i != n - 1) ? n - 2 : n - 3;
            int resL = -1;
            while (L <= R) {
                int m = (L + R) / 2;
                int pf = queryGcd(0, m, i);
                int suff = queryGcd(m + 1, n - 1, i);
                if (pf == suff) {
                    resL = m;
                    R = m - 1;
                } else if (pf < suff) {
                    R = m - 1;
                } else {
                    L = m + 1;
                }
            }
            if (resL == -1) {
                continue;
            }
            L = (i != 0) ? 0 : 1;
            R = (i != n - 1) ? n - 2 : n - 3;
            int resR = -1;
            while (L <= R) {
                int m = (L + R) / 2;
                int pf = queryGcd(0, m, i);
                int suff = queryGcd(m + 1, n - 1, i);
                if (pf == suff) {
                    resR = m;
                    L = m + 1;
                } else if (pf < suff) {
                    R = m - 1;
                } else {
                    L = m + 1;
                }
            }
            int width = resR - resL + 1;
            if (resL <= i && resR >= i) {
                width -= 1;
            }
            res = max(res, width);
        }

        // one final check where we remove nothing
        int removeNone = 0;
        for (int i = 0; i < n - 1; i++) {
            int lh = st.query(0, i);
            int rh = st.query(i + 1, n - 1);
            removeNone += (lh == rh);
        }
        res = max(res, removeNone);
        return res;
    }
};