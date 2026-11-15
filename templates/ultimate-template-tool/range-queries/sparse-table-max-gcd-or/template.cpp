// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-max-gcd-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: gcdAll maxAll orAll pointGet rangeGcd rangeMax rangeOrQuery
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeGcd: log(U) ?
//   rangeMax: 1
//   rangeOrQuery: 1
//   maxAll: 1
//   gcdAll: log(U) ?
//   orAll: 1
//   build: N*log(N)*log(U) ?
// @memory:
//   layout: none
//   node: mx[1*N*log(N)] g[1*N*log(N)] orr[1*N*log(N)]
//   tags: none
//   other: none
//   note: one table per aggregate (max, gcd, OR), each log(N) levels of up to N values; level 0 is the array itself

// Static range max, gcd and OR in one class: one sparse table per aggregate. Level k of a table holds that aggregate
// of every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one
// starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when a value
// is counted twice). No updates. All indices 0-based, ranges inclusive. A gcd is a Euclid run, O(log U), so rangeGcd
// costs one of those and the build N log N of them.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseMaxGcdOr {
    int n;
    // one table per aggregate: tab[k][i] = that aggregate of a[i .. i + 2^k - 1]
    vector<vector<T>> mx, g, orr;

    static T mxOf(T a, T b) { return a > b ? a : b; }
    static T gOf(T a, T b) { return std::gcd(a, b); }
    static T orrOf(T a, T b) { return a | b; }

    // O(N log N log U) -- N log N gcds, each up to O(log U)
    explicit SparseMaxGcdOr(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        mx.assign(levels, vector<T>());
        mx[0] = a;
        g.assign(levels, vector<T>());
        g[0] = a;
        orr.assign(levels, vector<T>());
        orr[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            mx[k].resize(len);
            for (int i = 0; i < len; i++) mx[k][i] = mxOf(mx[k - 1][i], mx[k - 1][i + half]);
            g[k].resize(len);
            for (int i = 0; i < len; i++) g[k][i] = gOf(g[k - 1][i], g[k - 1][i + half]);
            orr[k].resize(len);
            for (int i = 0; i < len; i++) orr[k][i] = orrOf(orr[k - 1][i], orr[k - 1][i + half]);
        }
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return mx[0][i];
    }

    // O(1) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return mxOf(mx[k][l], mx[k][r - (1 << k) + 1]);
    }

    // O(log U) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0); needs 0 <= l <= r < n, else throws out_of_range
    T rangeGcd(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return gOf(g[k][l], g[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeOrQuery(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return orrOf(orr[k][l], orr[k][r - (1 << k) + 1]);
    }

    // O(1) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws out_of_range
    auto gcdAll() {
        if (n < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, n - 1);
    }

    // O(1) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

};
