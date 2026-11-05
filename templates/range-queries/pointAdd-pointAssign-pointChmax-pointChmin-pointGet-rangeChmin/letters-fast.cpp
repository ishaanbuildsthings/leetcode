// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeChmin/letters-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAssign pointChmax pointChmin pointGet rangeChmin
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: 1
//   pointGet: log(N)
//   rangeChmin: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeChmin tag (no aggregates); leaves count as node data, internal nodes as tags

// Letters version: the values are characters (Python: a list of characters, e.g. list(s); C++: T = char), and only the
// operations that make sense on characters are listed.
// rangeChmin + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
// rangeChmin composes with itself in any order, so a range update only tags the O(logN) covering nodes and
// pointGet folds the tags on the leaf-to-root path. Only overwrites (pointAssign etc.) push those tags off
// the path first, so they aren't re-applied to the new value. T: int, long long, ...
// FAST MODE drawbacks compared with letters.cpp:
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct RangeChminTree {
    int n;
    HotVector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending tag (identity numeric_limits<T>::max())

    // O(N)
    explicit RangeChminTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), numeric_limits<T>::max()) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    // O(logN) -- a[i] = min(a[i], v) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeChmin(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeChmin: needs 0 <= l <= r < n");
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) { tree[l] = (tree[l] < v ? tree[l] : v); l++; }
            if (r & 1) { --r; tree[r] = (tree[r] < v ? tree[r] : v); }
        }
    }

    // O(logN) -- move the tags on leaf p's root-to-leaf path down, so nothing above p is pending
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            T t = tree[x];
            if (t != numeric_limits<T>::max()) {
                tree[2 * x] = (tree[2 * x] < t ? tree[2 * x] : t);
                tree[2 * x + 1] = (tree[2 * x + 1] < t ? tree[2 * x + 1] : t);
                tree[x] = numeric_limits<T>::max();
            }
        }
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        T a = tree[p];
        for (p >>= 1; p; p >>= 1) a = (a < tree[p] ? a : tree[p]);
        return a;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) {
            T t = tree[x];
            if (t != numeric_limits<T>::max()) {
                tree[2 * x] = (tree[2 * x] < t ? tree[2 * x] : t);
                tree[2 * x + 1] = (tree[2 * x + 1] < t ? tree[2 * x + 1] : t);
                tree[x] = numeric_limits<T>::max();
            }
        }
        return vector<T>(tree.begin() + n, tree.end());
    }

    // O(logN) -- a[i] = val; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tree[p] = val;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tree[p] = tree[p] + delta;
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        push(p);
        if (v > tree[p]) tree[p] = v;
    }

    // O(1) -- a[i] = min(a[i], v); a leaf-level chmin tag commutes with the pending ones above it; needs 0 <= i < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        if (v < tree[p]) tree[p] = v;
    }
};
