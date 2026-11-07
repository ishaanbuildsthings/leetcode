// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeMod
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeMod: log(N)*log(U) amortized
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: mx[2*N]
//   tags: none
//   other: none
//   note: mx[n:] holds the values, mx[1:n] the max of each node's subtree; there are no tags at all

// Range mod + point ops. All indices 0-based, ranges inclusive [l, r]. Requires a[i] >= 0, mod >= 1.
// Mods don't compose into a single tag, so rangeMod walks down into every covering node whose max is still
// >= mod. Each value that actually changes at least halves, so the work is amortized O((N + Q) logN logU).
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct RangeModTree {
    int n;
    HotVector<T> mx;  // mx[n + i] = a[i]; mx[1 .. n-1] = max of the subtree
    HotVector<int> stack, inner;

    // O(N)
    explicit RangeModTree(const vector<T>& a) : n((int)a.size()), mx(2 * a.size()) {
        for (int i = 0; i < n; i++) mx[n + i] = a[i];
        for (int i = n - 1; i > 0; i--) mx[i] = max(mx[2 * i], mx[2 * i + 1]);
    }

    // O(logN) -- recompute the maxes on leaf p's path to the root
    LEETCODE_NO_SANITIZE void pull(int p) {
        for (p >>= 1; p; p >>= 1) mx[p] = max(mx[2 * p], mx[2 * p + 1]);
    }

    LEETCODE_NO_SANITIZE void descend(int top, T mod) {
        stack.assign(1, top);
        inner.clear();
        while (!stack.empty()) {
            int y = stack.back();
            stack.pop_back();
            if (mx[y] < mod) continue;
            if (y >= n) mx[y] %= mod;
            else inner.push_back(y), stack.push_back(2 * y), stack.push_back(2 * y + 1);
        }
        // pre-order reversed puts every child before its parent
        for (int k = (int)inner.size() - 1; k >= 0; k--) {
            int y = inner[k];
            mx[y] = max(mx[2 * y], mx[2 * y + 1]);
        }
    }

    // amortized O(logN logU) -- a[i] %= mod for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMod(int l, int r, T mod) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMod: needs 0 <= l <= r < n");
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) descend(lo++, mod);
            if (hi & 1) descend(--hi, mod);
        }
        pull(l + n), pull(r + n);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return mx[i + n];
    }

    // O(N) -- the whole array (a copy of the leaves)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return vector<T>(mx.begin() + n, mx.end()); }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        mx[i + n] = v; pull(i + n);
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        mx[i + n] += delta; pull(i + n);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > mx[i + n]) mx[i + n] = v, pull(i + n);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < mx[i + n]) mx[i + n] = v, pull(i + n);
    }
};
