// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-min-max-and/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll maxAll minAll pointGet rangeAndQuery rangeMax rangeMin
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeAndQuery: 1
//   rangeMax: 1
//   rangeMin: 1
//   minAll: 1
//   maxAll: 1
//   andAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: mn[1*N*log(N)] mx[1*N*log(N)] an[1*N*log(N)]
//   tags: none
//   other: none
//   note: one table per aggregate (min, max, AND), each log(N) levels of up to N values; level 0 is the array itself

// Static range min, max and AND in one class: one sparse table per aggregate. Level k of a table holds that aggregate
// of every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one
// starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when a value is
// counted twice). No updates. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseMinMaxAnd {
    int n;
    // one table per aggregate: tab[k][i] = that aggregate of a[i .. i + 2^k - 1]
    vector<vector<T>> mn, mx, an;

    static T mnOf(T a, T b) { return a < b ? a : b; }
    static T mxOf(T a, T b) { return a > b ? a : b; }
    static T anOf(T a, T b) { return a & b; }

    // O(N log N)
    explicit SparseMinMaxAnd(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        mn.assign(levels, vector<T>());
        mn[0] = a;
        mx.assign(levels, vector<T>());
        mx[0] = a;
        an.assign(levels, vector<T>());
        an[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            mn[k].resize(len);
            for (int i = 0; i < len; i++) mn[k][i] = mnOf(mn[k - 1][i], mn[k - 1][i + half]);
            mx[k].resize(len);
            for (int i = 0; i < len; i++) mx[k][i] = mxOf(mx[k - 1][i], mx[k - 1][i + half]);
            an[k].resize(len);
            for (int i = 0; i < len; i++) an[k][i] = anOf(an[k - 1][i], an[k - 1][i + half]);
        }
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return mn[0][i];
    }

    // O(1) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMin(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return mnOf(mn[k][l], mn[k][r - (1 << k) + 1]);
    }

    // O(1) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return mxOf(mx[k][l], mx[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeAndQuery(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return anOf(an[k][l], an[k][r - (1 << k) + 1]);
    }

    // O(1) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(1) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(1) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

};
