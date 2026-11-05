// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: 1
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: stamp[1*N] val[1*N]
//   tags: stamp[1*N] val[1*N]
//   other: none
//   note: every node remembers the last assignment that covered it and when; a point takes the newest one on its path; leaves count as node data, internal nodes as tags

// Range assign + point ops, no pushing anywhere. All indices 0-based, ranges inclusive [l, r].
// Assignments are stamped with an increasing counter; pointGet returns the value with the largest stamp
// among the leaf and its ancestors. A point write is just a newer stamp on the leaf, so it is O(1).
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
struct RangeAssignTree {
    int n, clock = 0;
    HotVector<int> stamp;  // stamp[x] = when node x was last assigned (-1 never, leaves start at 0)
    HotVector<T> val;      // val[x] = what it was assigned to; val[n + i] starts as a[i]

    // O(N)
    explicit RangeAssignTree(const vector<T>& a) : n((int)a.size()), stamp(2 * a.size(), -1), val(2 * a.size()) {
        for (int i = 0; i < n; i++) stamp[n + i] = 0, val[n + i] = a[i];
    }

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        int c = ++clock;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) stamp[l] = c, val[l] = v, l++;
            if (r & 1) --r, stamp[r] = c, val[r] = v;
        }
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n, best = stamp[p];
        T res = val[p];
        for (p >>= 1; p; p >>= 1)
            if (stamp[p] > best) best = stamp[p], res = val[p];
        return res;
    }

    // O(N) -- the whole array: hand each node's assign to its children when it is newer than theirs (a parent's
    // index is below its children's, so in index order each node already holds the newest assign on its path)
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 2; x < 2 * n; x++)
            if (stamp[x >> 1] > stamp[x]) stamp[x] = stamp[x >> 1], val[x] = val[x >> 1];
        return vector<T>(val.begin() + n, val.end());
    }

    // O(1) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        stamp[i + n] = ++clock, val[i + n] = v;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
