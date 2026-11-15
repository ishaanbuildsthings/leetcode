// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/sparse-table-gcd-and/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll gcdAll pointGet rangeAndQuery rangeGcd
// @data-structure-type: sparse-table
// @complexities:
//   pointGet: 1
//   rangeAndQuery: 1
//   rangeGcd: log(U) ?
//   gcdAll: log(U) ?
//   andAll: 1
//   build: N*log(N)*log(U) ?
// @memory:
//   layout: none
//   node: g[1*N*log(N)] an[1*N*log(N)]
//   tags: none
//   other: none
//   note: one table per aggregate (gcd, AND), each log(N) levels of up to N values; level 0 is the array itself

// Static range gcd and AND in one class: one sparse table per aggregate. Level k of a table holds that aggregate of
// every window of 2^k values, and a range is the combine of the two largest power-of-two windows that fit, one
// starting at l and one ending at r (they overlap, which is fine: each of these gives the same answer when a value
// is counted twice). No updates. All indices 0-based, ranges inclusive. A gcd is a Euclid run, O(log U), so rangeGcd
// costs one of those and the build N log N of them.
// T is any integral type (int, long long, ...).
// FAST MODE drawbacks compared with template.cpp:
//   - sanitizers are skipped inside this template, so a bad access in it goes unreported
// Same public operations and answers, same limits; it needs GCC or Clang and C++17.
#ifdef __SSE2__
#include <immintrin.h>
#endif

// LEETCODE_NO_SANITIZE skips sanitizers in a function. It only changes anything where sanitizers run, like LeetCode: on
// Codeforces it compiles and does nothing.
// This template already uses it. To go further, put it on the one function with your hot loop:
//   LEETCODE_NO_SANITIZE long long maxSum(vector<int>& nums, int k) {
// A lambda needs its own: [&](int x) LEETCODE_NO_SANITIZE { ... }. It does not carry into anything that function calls.
// Inside a marked function use raw pointers and plain comparisons, not vector[] and min / max, or it can get slower.
// Bad memory accesses in a marked function go unreported.
#ifndef LEETCODE_NO_SANITIZE
#define LEETCODE_NO_SANITIZE __attribute__((no_sanitize("address"), no_sanitize("undefined")))
#endif
#define LEETCODE_NO_SANITIZE_INLINE LEETCODE_NO_SANITIZE __attribute__((always_inline)) inline

// A vector whose [] and size() always inline, even with sanitizers skipped (libstdc++ only; elsewhere a plain vector)
template <typename U>
struct HotVector : vector<U> {
    using vector<U>::vector;
    HotVector() = default;
    HotVector(const vector<U>& other) : vector<U>(other) {}
    HotVector(vector<U>&& other) : vector<U>(move(other)) {}
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseGcdAnd {
    int n;
    // one table per aggregate: tab[k][i] = that aggregate of a[i .. i + 2^k - 1]
    HotVector<vector<T>> g, an;

    LEETCODE_NO_SANITIZE static T gOf(T a, T b) { return std::gcd(a, b); }
    LEETCODE_NO_SANITIZE static T anOf(T a, T b) { return a & b; }

    // O(N log N log U) -- N log N gcds, each up to O(log U)
    explicit SparseGcdAnd(const vector<T>& a) : n((int)a.size()) {
        int levels = n ? 32 - __builtin_clz(n) : 1;
        g.assign(levels, vector<T>());
        g[0] = a;
        an.assign(levels, vector<T>());
        an[0] = a;
        for (int k = 1; k < levels; k++) {
            int half = 1 << (k - 1), len = n - (1 << k) + 1;
            g[k].resize(len);
            for (int i = 0; i < len; i++) g[k][i] = gOf(g[k - 1][i], g[k - 1][i + half]);
            an[k].resize(len);
            for (int i = 0; i < len; i++) an[k][i] = anOf(an[k - 1][i], an[k - 1][i + half]);
        }
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return g[0][i];
    }

    // O(log U) -- gcd of |a[l]|, ..., |a[r]| (0 only if all are 0); needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeGcd(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return gOf(g[k][l], g[k][r - (1 << k) + 1]);
    }

    // O(1) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        int k = 31 - __builtin_clz(r - l + 1);
        return anOf(an[k][l], an[k][r - (1 << k) + 1]);
    }

    // O(log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto gcdAll() {
        if (n < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, n - 1);
    }

    // O(1) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

};
