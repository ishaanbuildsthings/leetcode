// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointGet-rangeGcd/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: gcdAll pointGet rangeGcd
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeGcd: log(U) ?
//   gcdAll: log(U) ?
//   build: N*log(N)*log(U) ?
// @memory:
//   layout: none
//   node: sparse[1*N*log(N)]
//   tags: none
//   other: none
//   note: log(N) levels of N values each; level 0 is the array itself
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/sparse-tables/SparseGCD.cpp

// Static rangeGcd: sparse table, overlapping power-of-two windows. All indices 0-based, ranges inclusive.
// T is any integral type (int, long long, ...).
template <typename T>
struct SparseGcd {
    int n;
    vector<vector<T>> sp;  // sp[k][i] = combine of a[i .. i + 2^k - 1]

    static T combine(T a, T b) { return std::gcd(a, b); }

    // O(N log N log U) -- N log N gcds, each up to O(log U)
    explicit SparseGcd(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        sp.assign(levels, vector<T>());
        sp[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            sp[k].resize(max(len, 0));
            for (int i = 0; i < len; i++) sp[k][i] = combine(sp[k - 1][i], sp[k - 1][i + half]);
        }
    }

    // O(logU) because of the gcd call, O(1) -- gcd of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeGcd(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return combine(sp[k][l], sp[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return sp[0][i];
    }

    // O(log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws out_of_range
    auto gcdAll() {
        if (n < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, n - 1);
    }

};
