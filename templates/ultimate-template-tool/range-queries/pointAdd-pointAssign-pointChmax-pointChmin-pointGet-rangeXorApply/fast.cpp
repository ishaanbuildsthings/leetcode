// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeXorApply/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeXorApply
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeXorApply: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: a Fenwick tree over the xor-difference array; a[i] is the prefix xor of differences up to i

// Range xor, point get: a Fenwick tree over the xor-difference array. 0-based, inclusive. T: integral.
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct RangeXorBIT {
    int n;
    HotVector<T> tree;  // 1-indexed, over d[i] = a[i] ^ a[i - 1]

    // O(N)
    explicit RangeXorBIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        T prev = 0;
        for (int i = 1; i <= n; i++) {
            tree[i] ^= a[i - 1] ^ prev;
            prev = a[i - 1];
            int j = i + (i & -i);
            if (j <= n) tree[j] ^= tree[i];
        }
    }

    LEETCODE_NO_SANITIZE void apply(int i, T x) {
        for (i++; i <= n; i += i & -i) tree[i] ^= x;
    }

    // O(logN) -- a[i] ^= x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorApply: needs 0 <= l <= r < n");
        apply(l, x);
        if (r + 1 < n) apply(r + 1, x);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        T s = 0;
        for (i++; i > 0; i &= i - 1) s ^= tree[i];
        return s;
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete), then one pass of running prefix sums
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> d(tree), out(n);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) d[j] ^= d[i];
        }
        T s = 0;
        for (int i = 0; i < n; i++) out[i] = s ^= d[i + 1];
        return out;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        T d = pointGet(i) ^ v;
        if (d) rangeXorApply(i, i, d);
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) rangeXorApply(i, i, cur ^ v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) rangeXorApply(i, i, cur ^ v);
    }
};
