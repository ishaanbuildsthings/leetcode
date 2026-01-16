// Construct an AND sparse table

// O(n log n) build time
// O(1) query range AND
// ✅ Passed a question
// ⚠️ Not optimized, also my style is a bit weird as I populate sparse[power][left] even when it would go past the right edge, might be slower to build

#include <bits/stdc++.h>
using namespace std;

struct Sparse {
    int n;
    int LOG;
    vector<vector<int>> sparse; // sparse[power][left] is the AND for that range
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
                int andLeft = sparse[power-1][left];
                int rightEdge = left + halfWidth;
                if (rightEdge < n) {
                    andLeft &= sparse[power-1][rightEdge];
                }
                sparse[power][left] = andLeft;
            }
        }
    }
    int query(int l, int r) {
        int width = r - l + 1;
        int maxPow = 31 - __builtin_clz(width);
        int powWidth = 1 << maxPow;
        int left = sparse[maxPow][l];
        int right = sparse[maxPow][l + width - powWidth];
        return left & right;
    }
};