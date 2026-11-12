// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-rangeAdd-rangeAddArithSeq/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd rangeAdd rangeAddArithSeq
// @data-structure-type: difference-array
// @complexities:
//   getAll: N
//   pointAdd: 1
//   rangeAdd: 1
//   rangeAddArithSeq: 1
//   build: N
// @memory:
//   layout: none
//   node: dk[1*N] ds[1*N]
//   tags: none
//   other: a[1*N]
//   note: every add is a line k + s * i over [l, r]; dk and ds are difference arrays of k and s, and getAll sweeps both

// Range add and arithmetic sequence add, then read the array: two difference arrays (a double sweep line). An add of
// start, start + step, ... over [l, r] is the line k + step * i with k = start - l * step, so it is O(1): k and step go
// into one difference array each, and getAll sweeps both and adds k + step * i at every i, O(N). getAll can be called
// again later (the adds are kept). Nothing reads a single value in between: for that, use a BIT or seg tree. All
// indices 0-based, ranges inclusive [l, r].
// T: int, long long, ...
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
struct DiffArrayArith {
    int n;
    HotVector<T> a, dk, ds;

    // O(N) -- arr: the initial array (can be empty)
    explicit DiffArrayArith(const vector<T>& arr) : n((int)arr.size()), a(arr), dk(n + 1), ds(n + 1) {}

    // O(1) -- a[l + j] += start + j * step for j in [0, r - l]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAddArithSeq(int l, int r, T start, T step) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAddArithSeq: needs 0 <= l <= r < n");
        T k = start - T(l) * step;
        dk[l] += k;
        dk[r + 1] -= k;
        ds[l] += step;
        ds[r + 1] -= step;
    }

    // O(1) -- a[i] += v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        dk[l] += v;
        dk[r + 1] -= v;
    }

    // O(1) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        dk[i] += v;
        dk[i + 1] -= v;
    }

    // O(N) -- the whole array with every add so far applied (a new vector)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(a);
        T k = 0, s = 0;
        for (int i = 0; i < n; i++) {
            k += dk[i];
            s += ds[i];
            out[i] += k + s * T(i);
        }
        return out;
    }
};
