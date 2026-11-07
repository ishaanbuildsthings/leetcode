// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeOrApply-rangeXorApply/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeOrApply rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAndApply: log(N)
//   rangeOrApply: log(N)
//   rangeXorApply: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: val[1*N]
//   tags: AND[1*N] XOR[1*N]
//   other: none
//   note: each internal node holds one pending bit map x -> (x & AND) ^ XOR; val holds the leaf values

// Range and / or / xor + point ops, no range aggregates. All indices 0-based, ranges inclusive [l, r].
// Every update is a bit map (a, x): v -> (v & a) ^ x, and they compose into one:
//   and v -> (v, 0)    or v -> (~v, v)    xor v -> (~0, v)
// They don't commute (and then xor != xor then and), so the paths to l and r are pushed before tagging.
// T: any integral type, signed or unsigned.
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
struct BitOpTree {
    static constexpr T ALL = T(~T(0));
    int n;
    HotVector<T> AND, XOR;  // internal nodes 1 .. n-1: pending map v -> (v & AND) ^ XOR
    HotVector<T> val;       // leaf values

    // O(N)
    explicit BitOpTree(const vector<T>& a) : n((int)a.size()), AND(a.size(), ALL), XOR(a.size(), 0), val(a) {}

    // apply (a, x) on top of whatever node y already holds
    LEETCODE_NO_SANITIZE void apply(int y, T a, T x) {
        if (y >= n) {
            val[y - n] = (val[y - n] & a) ^ x;
            return;
        }
        AND[y] &= a;
        XOR[y] = (XOR[y] & a) ^ x;
    }

    // O(logN) -- push every pending tag on leaf p's root-to-leaf path down to its children
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            
            if (!(AND[x] == ALL && XOR[x] == 0)) {
                apply(2 * x, AND[x], XOR[x]);
                apply(2 * x + 1, AND[x], XOR[x]);
                AND[x] = ALL, XOR[x] = 0;
            }
        }
    }
    LEETCODE_NO_SANITIZE void update(int l, int r, T a, T x) {
        l += n, r += n;
        push(l), push(r);
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, a, x);
            if (r & 1) apply(--r, a, x);
        }
    }

    // O(logN) -- a[i] &= v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAndApply(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndApply: needs 0 <= l <= r < n");
        update(l, r, v, 0);
    }

    // O(logN) -- a[i] |= v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeOrApply(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrApply: needs 0 <= l <= r < n");
        update(l, r, T(~v), v);
    }

    // O(logN) -- a[i] ^= v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeXorApply: needs 0 <= l <= r < n");
        update(l, r, ALL, v);
    }

    // O(logN) -- a[i]: apply ancestors' maps bottom-up (deeper tags are older); needs 0 <= i < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        T v = val[i];
        for (int p = (i + n) >> 1; p; p >>= 1) v = (v & AND[p]) ^ XOR[p];
        return v;
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (!(AND[x] == ALL && XOR[x] == 0)) {
                apply(2 * x, AND[x], XOR[x]), apply(2 * x + 1, AND[x], XOR[x]);
                AND[x] = ALL, XOR[x] = 0;
            }
        return val;
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        push(i + n); val[i] = v;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        push(i + n); val[i] = val[i] + delta;
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        push(i + n); if (v > val[i]) val[i] = v;
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        push(i + n); if (v < val[i]) val[i] = v;
    }
};
