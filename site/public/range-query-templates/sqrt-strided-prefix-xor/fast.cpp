// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/sqrt-strided-prefix-xor/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: stridedXorQuery
// @data-structure-type: sqrt
// @complexities:
//   stridedXorQuery: sqrt(N)
//   build: 1*N*sqrt(N)
// @memory:
//   layout: none
//   node: xorPre[1*N*sqrt(N)]
//   tags: none
//   other: A[1*N]
//   note: O(1) for a step up to the cutoff, sqrt(N) only for a bigger one. The default cutoff is about 90 million values at N = 2e5, so pass a lower one when memory is tight

// Static strided queries, every small stride's prefix array built up front: each query covers a[l], a[l + step],
// a[l + 2 * step], ... up to at most r (the last position used may be below r). All indices 0-based, ranges inclusive.
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
struct StridedQueries {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, strides;
    HotVector<T> A;
    HotVector<T> xorPre;

    // O(build) -- arr: the initial array. cutoff: prefix arrays are kept for steps up to it; leave it out for sqrt(n), and
    // lower it when memory is tight (each kept step costs n values)
    explicit StridedQueries(const vector<T>& arr, int cutoff = -1) {
        n = (int)arr.size();
        A = arr;
        strides = cutoff != -1 ? cutoff : max(1, min(n, (int)sqrt((double)n)));
        if (strides < 0 || strides > n) throw out_of_range("StridedQueries: needs 0 <= cutoff <= n");
        xorPre.assign((size_t)strides * n, 0);
        for (int step = 1; step <= strides; step++) {
            T* pre = xorPre.data() + (size_t)(step - 1) * n;
            for (int i = 0; i < n; i++) pre[i] = (i >= step ? pre[i - step] : T(0)) ^ A[i];
        }
    }

    // a[l] ^ a[l + step] ^ ..., up to at most r. O(1) for a kept step; needs 0 <= l <= r < n and step >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE T stridedXorQuery(int l, int r, int step) {
        if (l < 0 || l > r || r >= n || step < 1) throw out_of_range("stridedXorQuery: needs 0 <= l <= r < n and step >= 1");
        int last = l + (r - l) / step * step;
        if (step > strides) {
            T res = 0;
            for (int i = l; i <= last; i += step) res ^= A[i];
            return res;
        }
        const T* pre = xorPre.data() + (size_t)(step - 1) * n;
        return pre[last] ^ (l >= step ? pre[l - step] : T(0));
    }
};
