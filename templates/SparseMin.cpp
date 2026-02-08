// Construct a MIN sparse table
// O(n log n) build time
// O(1) query range MIN

#include <bits/stdc++.h>
using namespace std;

struct SparseMin {
    int n;
    int LOG;
    vector<vector<int>> sparse;

    SparseMin(const vector<int>& arr) {
        n = arr.size();
        LOG = 32 - __builtin_clz(n);
        sparse.resize(LOG, vector<int>(n));
        for (int i = 0; i < n; i++) {
            sparse[0][i] = arr[i];
        }
        for (int power = 1; power < LOG; power++) {
            int halfWidth = 1 << (power - 1);
            for (int left = 0; left < n; left++) {
                int val = sparse[power - 1][left];
                int rightEdge = left + halfWidth;
                if (rightEdge < n) {
                    val = min(val, sparse[power - 1][rightEdge]);
                }
                sparse[power][left] = val;
            }
        }
    }

    int query(int l, int r) {
        int width = r - l + 1;
        int maxPow = 31 - __builtin_clz(width);
        int powWidth = 1 << maxPow;
        return min(
            sparse[maxPow][l],
            sparse[maxPow][l + width - powWidth]
        );
    }
};
