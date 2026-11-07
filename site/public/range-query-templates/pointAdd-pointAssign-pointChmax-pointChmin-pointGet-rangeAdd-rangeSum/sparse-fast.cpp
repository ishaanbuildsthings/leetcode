// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeSum/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeSum
// @data-structure-type: BIT
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: A[2*log(U)] B[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per update, the O(logU) entries above each changed position; a range add changes two points of A and B. A dynamic prefix-sum tree in a node pool the tree owns

// Range add + range sum: adding v on [l, r] changes the prefix sum P(x) = a[lo] + ... + a[x] by
//   v * (x - l + 1) for x in [l, r], and the whole v * (r - l + 1) past r,
// so P(x) = A(x) + B(x) * x with A, B prefix sums of two arrays of point changes. Over any index range [lo, hi] (huge
// or negative is fine); every position starts at 0. Sparse: a dynamic prefix-sum tree over offsets x = i - lo in [0,
// n), in a pool the tree owns; node 0 is the all-zeros block. T: int, long long, ...
// FAST MODE drawbacks compared with sparse.cpp:
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
struct SparseRangeAddSumBIT {
    using W = unsigned long long;  // wraps mod 2^64: results are exact whenever they fit in long long
    using F = array<W, 2>;
    struct Node { F f; int l, r; };  // f: totals of the point changes under the node
    HotVector<Node> pool{Node{}};  // node 0: all zeros, its children are itself
    long long lo, hi, n;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddSumBIT(long long lo, long long hi) : lo(lo), hi(hi), n(hi - lo + 1) {}


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{});
        return (int)pool.size() - 1;
    }

    // O(logU) -- adds v at offset x: to every node on its root path
    LEETCODE_NO_SANITIZE void add(long long x, const F& v) {
        if (!root) root = make();
        int y = root;
        long long a = 0, b = n - 1;
        while (true) {
            F& f = pool[y].f;
            for (int j = 0; j < 2; j++) f[j] += v[j];
            if (a == b) return;
            long long m = a + (b - a) / 2;
            bool right = x > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
    }

    // O(logU) -- totals of the point changes at offsets 0..x (zeros for x < 0)
    LEETCODE_NO_SANITIZE F prefix(long long x) const {
        F s{};
        int y = x < 0 ? 0 : root;
        long long a = 0, b = n - 1;
        while (y) {
            if (b <= x) {  // the whole node is inside the prefix
                const F& f = pool[y].f;
                for (int j = 0; j < 2; j++) s[j] += f[j];
                break;
            }
            long long m = a + (b - a) / 2;
            if (x <= m) y = pool[y].l, b = m;
            else {
                const F& f = pool[pool[y].l].f;
                for (int j = 0; j < 2; j++) s[j] += f[j];
                y = pool[y].r, a = m + 1;
            }
        }
        return s;
    }

    // O(logU) -- a[i] += v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(long long l, long long r, T v) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAdd: needs lo <= l <= r <= hi");
        if (l > r) return;
        l -= lo, r -= lo;
        W c = W(v), a = c * W(1 - l);
        add(l, F{a, c});
        if (r + 1 < n) add(r + 1, F{c * W(r - l + 1) - a, W(0) - c});
    }

    // O(logU) -- a[lo] + ... + a[lo + x] (0 for x = -1)
    LEETCODE_NO_SANITIZE W sum(long long x) const {
        F s = prefix(x);
        return s[0] + s[1] * W(x);
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rangeSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        return l <= r ? (long long)(sum(r - lo) - sum(l - 1 - lo)) : 0;
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return T(rangeSum(i, i));
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAdd(i, i, delta);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAdd(i, i, v - pointGet(i));
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        T cur = pointGet(i); if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        T cur = pointGet(i); if (v < cur) rangeAdd(i, i, v - cur);
    }
};
