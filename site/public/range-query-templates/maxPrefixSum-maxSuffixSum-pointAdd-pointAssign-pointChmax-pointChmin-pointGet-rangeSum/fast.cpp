// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/maxPrefixSum-maxSuffixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll maxPrefixSum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum sumAll
// @data-structure-type: seg-tree
// @letters: same
// @complexities:
//   getAll: N
//   maxPrefixSum: log(N)
//   maxSuffixSum: log(N)
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
//   node: sm[2*N] pre[2*N] suf[2*N]
//   tags: none
//   other: none
//   note: each node is (sum, best prefix, best suffix); the merge is not commutative, so a query folds a left and a right accumulator

// Max prefix sum and max suffix sum of a range, plus range sum, with point updates. All indices 0-based, ranges
// inclusive [l, r]. Maxima are over NON-EMPTY pieces; when the empty piece is allowed (answer >= 0), take max(0, ...).
// Iterative 2N tree. The merge is not commutative, so a query folds nodes into a left accumulator (left to right)
// and a right accumulator (right to left), then joins the two. Leaner than the max subarray tree: only
// (sm, pre, suf) per node. T: int, long long, ...; every sum is kept in S (long long for small T).
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
struct MaxPrefixSuffixSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Node { S sm, pre, suf; };
    int n;
    HotVector<Node> t;

    LEETCODE_NO_SANITIZE static Node leaf(T v) { return {S(v), S(v), S(v)}; }

    LEETCODE_NO_SANITIZE static Node merge(const Node& a, const Node& b) { return {a.sm + b.sm, max(a.pre, a.sm + b.pre), max(b.suf, b.sm + a.suf)}; }

    // O(N)
    explicit MaxPrefixSuffixSumTree(const vector<T>& a) : n((int)a.size()), t(2 * a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = leaf(a[i]);
        for (int x = n - 1; x > 0; x--) t[x] = merge(t[2 * x], t[2 * x + 1]);
    }

    // O(logN) -- (sm, pre, suf) of a[l..r], l <= r
    LEETCODE_NO_SANITIZE Node query(int l, int r) const {
        Node left{}, right{};
        bool lEmpty = true, rEmpty = true;
        for (l += n, r += n + 1; l < r; l >>= 1, r >>= 1) {
            if (l & 1) left = lEmpty ? t[l] : merge(left, t[l]), lEmpty = false, l++;
            if (r & 1) --r, right = rEmpty ? t[r] : merge(t[r], right), rEmpty = false;
        }
        if (rEmpty) return left;
        if (lEmpty) return right;
        return merge(left, right);
    }

    // O(logN) -- max over l <= i <= r of a[l] + ... + a[i]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S maxPrefixSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < n");
        return query(l, r).pre;
    }

    // O(logN) -- max over l <= i <= r of a[i] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S maxSuffixSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < n");
        return query(l, r).suf;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) const {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l <= r ? query(l, r).sm : S(0);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        t[p] = leaf(v);
        for (p >>= 1; p; p >>= 1) t[p] = merge(t[2 * p], t[2 * p + 1]);
    }

    // O(1) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) const {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return T(t[i + n].sm);
    }

    // O(N) -- the whole array (a copy of the leaves)
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = T(t[n + i].sm);
        return out;
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

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

};
