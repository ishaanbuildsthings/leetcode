// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeFloorDiv: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: tree[1*N]
//   tags: tree[1*N]
//   other: none
//   note: tree[n:] holds the values, tree[1:n] holds each node's pending divisor (product of divisions, capped); leaves count as node data, internal nodes as tags

// Range floor-divide + point ops. All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
// floor(floor(x / a) / b) == floor(x / (a * b)) for positive integers a, b and any integer x, so pending
// divisions are just a product. Products are capped at CAP = max(T): once a divisor exceeds every |value|,
// any larger divisor gives the same floor. Requires every divisor >= 1 and |a[i]| < CAP.
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
struct RangeFloorDivTree {
    static constexpr T CAP = numeric_limits<T>::max();
    int n;
    HotVector<T> tree;  // tree[n + i] = a[i]; tree[1 .. n-1] = pending divisor product (1 = none)

    LEETCODE_NO_SANITIZE static T floorDiv(T x, T d) { T q = x / d; return (x % d != 0 && x < 0) ? q - 1 : q; }
    LEETCODE_NO_SANITIZE static T mulCap(T a, T b) { return a > CAP / b ? CAP : a * b; }

    // O(N)
    explicit RangeFloorDivTree(const vector<T>& a) : n((int)a.size()), tree(2 * a.size(), T(1)) {
        for (int i = 0; i < n; i++) tree[n + i] = a[i];
    }

    LEETCODE_NO_SANITIZE void apply(int x, T d) { tree[x] = x >= n ? floorDiv(tree[x], d) : mulCap(tree[x], d); }

    // O(logN) -- a[i] = floor(a[i] / d) for i in [l, r], d >= 1; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorDiv(int l, int r, T d) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeFloorDiv: needs 0 <= l <= r < n");
        if (d == 1) return;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) apply(l++, d);
            if (r & 1) apply(--r, d);
        }
    }

    // O(logN) -- apply the divisors on leaf p's path, so nothing above p is pending
    LEETCODE_NO_SANITIZE void push(int p) {
        for (int h = 31 - __builtin_clz(p); h > 0; h--) {
            int x = p >> h;
            if (tree[x] != 1) apply(2 * x, tree[x]), apply(2 * x + 1, tree[x]), tree[x] = 1;
        }
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        T d = 1;
        for (int x = p >> 1; x; x >>= 1) d = mulCap(d, tree[x]);
        return floorDiv(tree[p], d);
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) {
            if (tree[x] != 1) apply(2 * x, tree[x]), apply(2 * x + 1, tree[x]), tree[x] = 1;
        }
        return vector<T>(tree.begin() + n, tree.end());
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        push(i + n); tree[i + n] = v;
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        push(i + n); tree[i + n] += delta;
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        push(i + n); if (v > tree[i + n]) tree[i + n] = v;
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        push(i + n); if (v < tree[i + n]) tree[i + n] = v;
    }
};
