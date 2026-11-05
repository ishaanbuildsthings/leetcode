// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeGcd/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   build: 1
// @memory:
//   layout: sparse
//   node: sum[2*log(U)] g[2*log(U)]
//   tags: none
//   other: children[4*log(U)]
//   note: per range add, the two root paths of the differences it changes; one tree over the differences keeps their sum (prefix sums are point values) and gcd; the gcd costs' second log is of the largest value. A node pool per tree (node 0 = all zeros)

// Range add + range gcd + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at
// 0. gcd(a[l], ..., a[r]) == gcd(a[l], a[l+1] - a[l], ..., a[r] - a[r-1]), and a range add only changes two adjacent
// differences. One sparse tree over the differences d[i] = a[i] - a[i-1] (d[lo] = a[lo]) keeps their sum (a prefix sum
// is a point value) and the gcd of their absolute values. Sparse: nodes in a pool the tree owns; node 0 is the block of
// zero differences. T: int, long long, ...
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
struct SparseRangeAddRangeGcd {
    struct Node { T sum, g; int l, r; };
    HotVector<Node> pool{Node{0, 0, 0, 0}};  // node 0: all-zero differences, its children are itself
    long long lo, hi;
    int root = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAddRangeGcd(long long lo, long long hi) : lo(lo), hi(hi) {}


    // optional -- reserve room for this many nodes up front (about 2 logU per range add)
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{0, 0, 0, 0});
        return (int)pool.size() - 1;
    }

    LEETCODE_NO_SANITIZE static T absT(T x) { return x < 0 ? -x : x; }

    // O(logU logV) -- d[i] += x
    LEETCODE_NO_SANITIZE void shiftDiff(long long i, T x) {
        if (!root) root = make();
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {
            path[d++] = y;
            long long m = a + (b - a) / 2;
            bool right = i > m;
            int c = right ? pool[y].r : pool[y].l;
            if (!c) {
                c = make();
                (right ? pool[y].r : pool[y].l) = c;
            }
            y = c;
            if (right) a = m + 1;
            else b = m;
        }
        pool[y].sum += x, pool[y].g = absT(pool[y].sum);
        while (d--) {
            Node& p = pool[path[d]];
            p.sum = pool[p.l].sum + pool[p.r].sum;
            p.g = std::gcd(pool[p.l].g, pool[p.r].g);
        }
    }

    // O(logU) -- d[lo] + ... + d[i], which is a[i]
    LEETCODE_NO_SANITIZE T prefix(long long i) const {
        T s = 0;
        int y = root;
        long long a = lo, b = hi;
        while (y) {
            if (a == b) { s += pool[y].sum; break; }
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else s += pool[pool[y].l].sum, y = pool[y].r, a = m + 1;
        }
        return s;
    }

    // gcd of |d[max(l, a)..min(r, b)]|
    LEETCODE_NO_SANITIZE T gcdOf(int x, long long a, long long b, long long l, long long r) const {
        if (!x) return 0;
        if (l <= a && b <= r) return pool[x].g;
        long long m = a + (b - a) / 2;
        T res = 0;
        if (l <= m) res = gcdOf(pool[x].l, a, m, l, r);
        if (r > m) res = std::gcd(res, gcdOf(pool[x].r, m + 1, b, l, r));
        return res;
    }

    // O(logU logV) -- adds x to every a[l..r], x may be negative; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAdd: needs lo <= l <= r <= hi");
        if (l > r) return;
        shiftDiff(l, x);
        if (r < hi) shiftDiff(r + 1, -x);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return prefix(i);
    }

    // O(logU + logV) -- gcd of a[l..r], always >= 0 (0 only if every value in the range is 0); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeGcd(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeGcd: needs lo <= l <= r <= hi");
        T res = absT(prefix(l));
        if (l < r) res = std::gcd(res, gcdOf(root, lo, hi, l + 1, r));
        return res;
    }

    // O(logU logV) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAdd(i, i, delta);
    }

    // O(logU logV) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAdd(i, i, v - prefix(i));
    }

    // O(logU logV) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        T cur = prefix(i); if (v > cur) rangeAdd(i, i, v - cur);
    }

    // O(logU logV) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        T cur = prefix(i); if (v < cur) rangeAdd(i, i, v - cur);
    }
};
