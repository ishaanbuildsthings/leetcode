// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorSqrt/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorSqrt
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)+log(log(U))
//   pointAssign: log(N)+log(log(U))
//   pointChmax: log(N)+log(log(U))
//   pointChmin: log(N)+log(log(U))
//   pointGet: log(N)+log(log(U))
//   rangeFloorSqrt: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds how many floor-sqrts are pending at each node (capped at 6); leaves count as node data, internal nodes as tags

// Range floor-sqrt + point ops. All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
// Pending sqrts on a node are just a count. Six floor-sqrts take any value below 2^64 down to 0 or 1, which
// are fixed points, so counts are capped at MAX_SQRTS. Requires a[i] >= 0.
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
struct RangeFloorSqrtTree {
    static constexpr T MAX_SQRTS = 6;
    int n;
    HotVector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending sqrt count

    LEETCODE_NO_SANITIZE static T isqrt(T x) {
        T r = (T)sqrtl((long double)x);
        while ((__int128)r * r > x) r--;
        while ((__int128)(r + 1) * (r + 1) <= x) r++;
        return r;
    }

    LEETCODE_NO_SANITIZE static T sqrtTimes(T v, T k) {
        for (; k > 0 && v > 1; k--) v = isqrt(v);
        return v;
    }

    // O(N)
    explicit RangeFloorSqrtTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), T(0)) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    LEETCODE_NO_SANITIZE void apply(int x, T k) {
        if (x >= n) tree[x] = sqrtTimes(tree[x], k);
        else tree[x] = min(tree[x] + k, MAX_SQRTS);
    }

    // O(logN) -- a[i] = floor(sqrt(a[i])) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorSqrt(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeFloorSqrt: needs 0 <= l <= r < n");
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, 1);
            if (r & 1) apply(--r, 1);
        }
    }

    // O(logN + loglogU) -- apply the pending sqrts on leaf p's path, so nothing above p is pending
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            if (tree[x]) apply(2 * x, tree[x]), apply(2 * x + 1, tree[x]), tree[x] = 0;
        }
    }

    // O(logN + loglogU) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        T k = 0;
        for (int x = p >> 1; x; x >>= 1) k += tree[x];
        return sqrtTimes(tree[p], min(k, MAX_SQRTS));
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) {
            if (tree[x]) apply(2 * x, tree[x]), apply(2 * x + 1, tree[x]), tree[x] = 0;
        }
        return vector<T>(tree.begin() + n, tree.end());
    }

    // O(logN + loglogU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        push(i + n); tree[i + n] = v;
    }

    // O(logN + loglogU) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        push(i + n); tree[i + n] += delta;
    }

    // O(logN + loglogU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        push(i + n); if (v > tree[i + n]) tree[i + n] = v;
    }

    // O(logN + loglogU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        push(i + n); if (v < tree[i + n]) tree[i + n] = v;
    }
};
