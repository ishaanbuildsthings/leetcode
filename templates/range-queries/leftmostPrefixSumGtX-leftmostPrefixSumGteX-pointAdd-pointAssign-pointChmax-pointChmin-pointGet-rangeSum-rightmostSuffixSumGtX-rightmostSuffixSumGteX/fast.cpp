// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostPrefixSumGtX-leftmostPrefixSumGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum-rightmostSuffixSumGtX-rightmostSuffixSumGteX/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll leftmostPrefixSumGtX leftmostPrefixSumGteX pointAdd pointAssign pointChmax pointChmin pointGet rangeSum rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: BIT
// @complexities:
//   getAll: N
//   leftmostPrefixSumGtX: log(N)
//   leftmostPrefixSumGteX: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeSum: log(N)
//   rightmostSuffixSumGtX: log(N)
//   rightmostSuffixSumGteX: log(N)
//   build: N
// @memory:
//   layout: none
//   node: tree[1*N]
//   tags: none
//   other: none
//   note: the prefix / suffix-sum searches binary-lift over the tree, so they need every a[i] >= 0

// Point add, range sum (Fenwick tree). All indices 0-based, ranges inclusive [l, r]. T: int, long long, ...
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
struct BIT {
    int n;
    HotVector<T> tree;  // 1-indexed

    // O(N) -- push each node into its parent once
    explicit BIT(const vector<T>& a) : n((int)a.size()), tree(n + 1) {
        for (int i = 1; i <= n; i++) tree[i] = a[i - 1];
        for (int i = 1; i <= n; i++) {
            int j = i + (i & -i);
            if (j <= n) tree[j] += tree[i];
        }
    }

    // O(logN) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        for (i++; i <= n; i += i & -i) tree[i] += delta;
    }

    // O(logN) -- a[0] + ... + a[i]
    LEETCODE_NO_SANITIZE T prefixSum(int i) const {
        T s = 0;
        for (i++; i > 0; i &= i - 1) s += tree[i];
        return s;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l > r ? T(0) : prefixSum(r) - (l ? prefixSum(l - 1) : T(0));
    }

    // O(logN) -- a[i] in one walk instead of two prefix sums; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        i++;
        T v = tree[i];
        int stop = i - (i & -i);
        for (i--; i > stop; i &= i - 1) v -= tree[i];
        return v;
    }

    // O(N) -- the whole array: undo the Fenwick sums on a copy (last index first: entry i was added into
    // i + lowbit(i) once complete)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> t(tree);
        for (int i = n; i > 0; i--) {
            int j = i + (i & -i);
            if (j <= n) t[j] -= t[i];
        }
        return vector<T>(t.begin() + 1, t.end());
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        pointAdd(i, v - pointGet(i));
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v > cur) pointAdd(i, v - cur);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        T cur = pointGet(i);
        if (v < cur) pointAdd(i, v - cur);
    }

    // O(logN) -- smallest i with a[0] + ... + a[i] >= target (> target if strict), or n if none.
    // Binary lifting: grow pos by powers of two while the prefix stays below target. Needs every a[i] >= 0.
    LEETCODE_NO_SANITIZE int prefixLowerBound(T target, bool strict) const {
        int pos = 0;
        T acc = 0;
        for (int step = n ? 1 << (31 - __builtin_clz(n)) : 0; step; step >>= 1) {
            int nxt = pos + step;
            if (nxt <= n) {
                T v = acc + tree[nxt];
                if (v < target || (strict && v == target)) pos = nxt, acc = v;
            }
        }
        return pos;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1. Needs every a[i] >= 0. e.g. on a 0/1 array,
    // leftmostPrefixSumGteX(0, n - 1, k) is the index of the k-th one.; needs 0 <= l <= r < n, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < n");
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, false));
        return i <= r ? i : -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1. Needs every a[i] >= 0.; needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < n");
        int i = max(l, prefixLowerBound((l ? prefixSum(l - 1) : T(0)) + x, true));
        return i <= r ? i : -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1. Needs every a[i] >= 0. That is the last i with
    // a[0] + ... + a[i - 1] <= prefixSum(r) - x: one binary lift.; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGteX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < n");
        T t = prefixSum(r) - x;
        if (t < 0) return -1;
        int i = min(r, prefixLowerBound(t, true));
        return i >= l ? i : -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1. Needs every a[i] >= 0.; needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGtX(int l, int r, T x) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < n");
        T t = prefixSum(r) - x;
        if (t <= 0) return -1;
        int i = min(r, prefixLowerBound(t, false));
        return i >= l ? i : -1;
    }
};
