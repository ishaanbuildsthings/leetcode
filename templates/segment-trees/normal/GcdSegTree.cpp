// TEMPLATE BY https://github.com/agrawalishaan
// You are welcome to use this template. Please keep the link in your contest code to prevent automatic detection of copied content. Templates are allowed. Thanks!

// GCD segment tree, bottom-up iterative.
// Build: O(n log(maxVal))
// Space: O(2n)
// Query/Update: O(log N) gcd calls
// Uses 0 as the identity, so gcd(0, x) == x. A stored 0 means "contributes nothing".
#include <bits/stdc++.h>
using namespace std;
class GcdSegmentTree {
    int n;
    vector<int> arr;
    vector<int> tree;

public:
    GcdSegmentTree(const vector<int>& a) {
        n = a.size();
        arr = a;
        tree.assign(2 * n, 0);
        for (int i = 0; i < n; i++) {
            tree[n + i] = arr[i];
        }
        for (int i = n - 1; i >= 1; i--) {
            tree[i] = gcd(tree[2 * i], tree[2 * i + 1]);
        }
    }

    ///////////////// PUBLIC METHODS START HERE /////////////////

    // Point OVERWRITE (not chmax/add): arr[index] becomes newVal.
    void updateAndMutateArray(int index, int newVal) {
        arr[index] = newVal;
        int i = index + n;
        tree[i] = newVal;
        i >>= 1;
        while (i >= 1) {
            int v = gcd(tree[2 * i], tree[2 * i + 1]);
            if (tree[i] == v) {
                break;
            }
            tree[i] = v;
            i >>= 1;
        }
    }

    // Inclusive range [l, r]. Requires l <= r. Returns 0 for an empty range.
    int query(int l, int r) {
        int res = 0;
        l += n;
        r += n + 1;
        while (l < r) {
            if (l & 1) {
                res = gcd(res, tree[l]);
                l += 1;
            }
            if (r & 1) {
                r -= 1;
                res = gcd(res, tree[r]);
            }
            l >>= 1;
            r >>= 1;
        }
        return res;
    }
};