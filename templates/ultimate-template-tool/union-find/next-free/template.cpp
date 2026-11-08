// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/next-free/template.cpp
// @operations: isFree nextFree prevFree take takeRange
// @data-structure-type: next-free
// @complexities:
//   isFree: α(N) amortized
//   nextFree: α(N) amortized
//   prevFree: α(N) amortized
//   take: α(N) amortized
//   takeRange: α(N) amortized
//   build: N
// @memory:
//   layout: none
//   node: nxt[1*N] prv[1*N]
//   tags: none
//   other: none
//   note: takeRange costs α(N) amortized per index it takes, so O(N α(N)) over every call together
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// NextFree nf(n);
// Indices 0..n-1 start free; take(i) / takeRange(l, r) use them up, and nextFree / prevFree jump straight to the
// nearest index still free (painting intervals, "assign each query to the first unused slot", ...)
struct NextFree {
    int n;
    vector<int> nxt;  // follow nxt to the first free index >= i (n: none)
    vector<int> prv;  // follow prv to (the last free index <= i - 1) + 1, shifted so 0 means none

    // O(n), every index 0..n-1 starts free
    explicit NextFree(int n) : n(n), nxt(n + 1), prv(n + 1) {
        iota(nxt.begin(), nxt.end(), 0);
        iota(prv.begin(), prv.end(), 0);
    }

    int up(int i) {
        while (nxt[i] != i) i = nxt[i] = nxt[nxt[i]];
        return i;
    }

    int down(int i) {
        while (prv[i] != i) i = prv[i] = prv[prv[i]];
        return i;
    }

    // O(α(n)) amortized, the smallest free index >= i, n if there's none; needs 0 <= i <= n, else out_of_range
    int nextFree(int i) {
        if (i < 0 || i > n) throw out_of_range("nextFree: needs 0 <= i <= n");
        return up(i);
    }

    // O(α(n)) amortized, the largest free index <= i, -1 if there's none; needs -1 <= i < n, else out_of_range
    int prevFree(int i) {
        if (i < -1 || i >= n) throw out_of_range("prevFree: needs -1 <= i < n");
        return down(i + 1) - 1;
    }

    // O(α(n)) amortized, true if i hasn't been taken; needs 0 <= i < n, else out_of_range
    bool isFree(int i) {
        if (i < 0 || i >= n) throw out_of_range("isFree: needs 0 <= i < n");
        return up(i) == i;
    }

    // O(α(n)) amortized, uses up index i (nothing if it was already taken); needs 0 <= i < n, else out_of_range
    void take(int i) {
        if (i < 0 || i >= n) throw out_of_range("take: needs 0 <= i < n");
        if (up(i) == i) nxt[i] = i + 1, prv[i + 1] = i;
    }

    // O((how many were free) * α(n)) amortized, so O(n α(n)) over every call: uses up every free index in l..r and
    // returns them in order; needs 0 <= l <= r < n, else out_of_range
    vector<int> takeRange(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("takeRange: needs 0 <= l <= r < n");
        vector<int> res;
        for (int i = up(l); i <= r; i = up(i + 1)) {
            res.push_back(i);
            nxt[i] = i + 1, prv[i + 1] = i;
        }
        return res;
    }
};
