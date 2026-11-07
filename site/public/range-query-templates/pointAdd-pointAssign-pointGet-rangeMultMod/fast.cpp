// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointGet-rangeMultMod/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointGet rangeMultMod
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointGet: log(N)
//   rangeMultMod: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending rangeMultMod tag (no aggregates); leaves count as node data, internal nodes as tags

// rangeMultMod + point ops with no range aggregates. All indices 0-based, ranges inclusive [l, r].
// rangeMultMod composes with itself in any order, so a range update only tags the O(logN) covering nodes and
// pointGet folds the tags on the leaf-to-root path. Only overwrites (pointAssign etc.) push those tags off
// the path first, so they aren't re-applied to the new value. T: int, long long, ...
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
struct RangeMultModTree {
    using W = conditional_t<sizeof(T) <= 4, long long, __int128>;
    int n;
    T mod;
    HotVector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending tag (identity T(1))

    // O(N)
    explicit RangeMultModTree(const vector<T>& a, T mod = 1000000007) : n((int)a.size()), mod(mod), tree(2 * a.size(), T(1)) {
        for (int i = 0; i < n; i++) tree[n + i] = T((a[i] % mod + mod) % mod);
    }

    // O(logN) -- a[i] = a[i] * m (% MOD) for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMultMod(int l, int r, T m) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMultMod: needs 0 <= l <= r < n");
        m = T((m % mod + mod) % mod);
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) { tree[l] = T(W(tree[l]) * m % mod); l++; }
            if (r & 1) { --r; tree[r] = T(W(tree[r]) * m % mod); }
        }
    }

    // O(logN) -- move the tags on leaf p's root-to-leaf path down, so nothing above p is pending
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            T t = tree[x];
            if (t != T(1)) {
                tree[2 * x] = T(W(tree[2 * x]) * t % mod);
                tree[2 * x + 1] = T(W(tree[2 * x + 1]) * t % mod);
                tree[x] = T(1);
            }
        }
    }

    // O(logN) -- a[i], in [0, mod); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        T a = tree[p];
        for (p >>= 1; p; p >>= 1) a = T(W(a) * tree[p] % mod);
        return a;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) {
            T t = tree[x];
            if (t != T(1)) {
                tree[2 * x] = T(W(tree[2 * x]) * t % mod);
                tree[2 * x + 1] = T(W(tree[2 * x + 1]) * t % mod);
                tree[x] = T(1);
            }
        }
        return vector<T>(tree.begin() + n, tree.end());
    }

    // O(logN) -- a[i] = val; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T val) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        val = T((val % mod + mod) % mod);
        int p = i + n;
        push(p);
        tree[p] = val;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        push(p);
        tree[p] = T(((W(tree[p]) + delta) % mod + mod) % mod);
    }
};
