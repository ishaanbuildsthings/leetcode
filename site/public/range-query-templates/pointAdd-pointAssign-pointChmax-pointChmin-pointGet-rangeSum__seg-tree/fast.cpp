// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum__seg-tree/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeSum sumAll
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: 1
//   rangeSum: log(N)
//   sumAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[2*N]
//   tags: none
//   other: none
//   note: tree holds each node's sum; leaves are tree[n..2n), no power-of-two padding; arr is a reference
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/pointAssignRangeSum.cpp

// Point update + rangeSum segment tree, iterative over 2N slots (leaves at tree[n..2n)).
// All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
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
struct SumSegTree {
    int n, size;
    HotVector<T> tree;  // tree[size + i] = a[i]; tree[x] = sum of x's children

    // O(N)
    explicit SumSegTree(const vector<T>& a) : n((int)a.size()), size(n) {
        tree.assign(2 * size, T(0));
        for (int i = 0; i < n; i++) tree[size + i] = a[i];
        for (int x = size - 1; x > 0; x--) tree[x] = tree[2 * x] + tree[2 * x + 1];
    }

    // O(logN) -- sum of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        T res = T(0);
        for (l += size, r += size + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = res + tree[l++];
            if (r & 1) res = res + tree[--r];
        }
        return res;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = size + i;
        tree[p] = v;
        for (p >>= 1; p; p >>= 1) tree[p] = tree[2 * p] + tree[2 * p + 1];
    }

    // O(logN) -- same as pointAssign, but also writes v into the array you pass in
    LEETCODE_NO_SANITIZE void pointAssignAndMutateArray(vector<T>& arr, int i, T v) {
        arr[i] = v;
        pointAssign(i, v);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return tree[size + i];
    }

    // O(N) -- the whole array (a copy of the leaves)
    LEETCODE_NO_SANITIZE vector<T> getAll() const { return vector<T>(tree.begin() + size, tree.begin() + size + n); }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > tree[size + i]) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < tree[size + i]) pointAssign(i, v);
    }

    // O(logN) -- a[i] += delta, by walking the delta up instead of recomputing nodes; needs 0 <= i < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        for (int p = size + i; p; p >>= 1) tree[p] += delta;
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

};
