// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-max-and-or/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll maxAll orAll pointGet rangeAndQuery rangeMax rangeOrQuery
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeAndQuery: 1
//   rangeMax: 1
//   rangeOrQuery: 1
//   maxAll: 1
//   andAll: 1
//   orAll: 1
//   build: N*log(N)
// @memory:
//   layout: none
//   node: mx[1*N*log(N)] an[1*N*log(N)] orr[1*N*log(N)]
//   tags: none
//   other: none
//   note: one table per aggregate (max, AND, OR), each log(N) levels of up to N values; level 0 is the array itself

// Static range max, AND and OR in one class: one sparse table per aggregate. Level k of a table holds that aggregate
// of every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one
// starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when a value
// is counted twice). No updates. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseMaxAndOr {
    int n;
    // one table per aggregate: tab[k][i] = that aggregate of a[i .. i + 2^k - 1]
    vector<vector<T>> mx, an, orr;

    static T mxOf(T a, T b) { return a > b ? a : b; }
    static T anOf(T a, T b) { return a & b; }
    static T orrOf(T a, T b) { return a | b; }

    // O(N log N)
    explicit SparseMaxAndOr(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        mx.assign(levels, vector<T>());
        mx[0] = a;
        an.assign(levels, vector<T>());
        an[0] = a;
        orr.assign(levels, vector<T>());
        orr[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            mx[k].resize(len);
            for (int i = 0; i < len; i++) mx[k][i] = mxOf(mx[k - 1][i], mx[k - 1][i + half]);
            an[k].resize(len);
            for (int i = 0; i < len; i++) an[k][i] = anOf(an[k - 1][i], an[k - 1][i + half]);
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

    // O(1) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeAndQuery(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return anOf(an[k][l], an[k][r - (1 << k) + 1]);
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

    // O(1) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // O(1) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

};
