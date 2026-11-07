// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/maxPrefixSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeSum/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: maxPrefixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeSum
// @data-structure-type: seg-tree
// @complexities:
//   maxPrefixSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[1*log(U)] pre[1*log(U)]
//   tags: none
//   other: children[2*log(U)]
//   note: per update, one node per level of the touched path; pieces are non-empty, so a block of zeros summarizes to all zeros; a node pool per tree (node 0 = all zeros)

// Max prefix sum + range sum with point updates, over any index range [lo, hi] (huge or negative is fine); every
// position starts at 0. Sparse: only the nodes on updated paths exist, in a pool the tree owns; a missing child is a
// block of zeros. Each node keeps the summary (sm, pre); merging is not commutative, so queries combine left to right.
// T: int, long long, ...; sums are kept in S (long long for small T).
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
struct SparseMaxPrefixSumTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // an impossible (first sign, last sign) pair
    struct Agg { S sm; S pre; };
    struct Node { Agg v; int l, r; };
    HotVector<Node> pool{Node{Agg{0, 0}, 0, 0}};  // node 0: the all-zeros block
    long long lo, hi;
    int root = 0;

    // O(1) -- an all-zero array over [lo, hi]; any long long range works
    SparseMaxPrefixSumTree(long long lo, long long hi) : lo(lo), hi(hi) {}


    // optional: reserve room for this many nodes up front (about log U per update)
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{Agg{0, 0}, 0, 0});
        return (int)pool.size() - 1;
    }

    // walk from the root to leaf i, creating missing nodes; fills path[] with the nodes above the leaf and
    // returns the leaf. len[] / starts[] (when given) receive each path node's range.
    LEETCODE_NO_SANITIZE int descend(long long i, int* path, int& depth, long long* starts = nullptr, long long* ends = nullptr) {
        if (!root) root = make();
        int x = root;
        long long a = lo, b = hi;
        depth = 0;
        while (a < b) {
            if (starts) starts[depth] = a, ends[depth] = b;
            path[depth++] = x;
            long long m = a + (b - a) / 2;
            if (i <= m) {
                if (!pool[x].l) { int y = make(); pool[x].l = y; }
                x = pool[x].l, b = m;
            } else {
                if (!pool[x].r) { int y = make(); pool[x].r = y; }
                x = pool[x].r, a = m + 1;
            }
        }
        return x;
    }

    // O(logU) -- the leaf for i, or 0 if no update has touched it
    LEETCODE_NO_SANITIZE int find(long long i) const {
        int x = root;
        long long a = lo, b = hi;
        while (x && a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) x = pool[x].l, b = m;
            else x = pool[x].r, a = m + 1;
        }
        return x;
    }

    LEETCODE_NO_SANITIZE static Agg merge(const Agg& a, const Agg& b) { return Agg{a.sm + b.sm, max(a.pre, a.sm + b.pre)}; }
    LEETCODE_NO_SANITIZE static Agg leaf(T v) { return Agg{S(v), S(v)}; }
    LEETCODE_NO_SANITIZE static Agg zero(long long len) { (void)len; return Agg{0, 0}; }  // a block of len zeros
    LEETCODE_NO_SANITIZE Agg agg(int x, long long len) { return pool[x].v; }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[130], depth;
        long long starts[130], ends[130];
        int x = descend(i, path, depth, starts, ends);
        pool[x].v = leaf(v);
        while (depth) {
            --depth;
            int y = path[depth];
            long long a = starts[depth], b = ends[depth], m = a + (b - a) / 2;
            pool[y].v = merge(agg(pool[y].l, m - a + 1), agg(pool[y].r, b - m));
        }
    }

    // summary of a[max(l, a)..min(r, b)]; [a, b] must overlap [l, r]
    LEETCODE_NO_SANITIZE Agg query(int x, long long a, long long b, long long l, long long r) const {
        if (!x) return zero(min(r, b) - max(l, a) + 1);
        if (l <= a && b <= r) return pool[x].v;
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r);
        if (l > m) return query(pool[x].r, m + 1, b, l, r);
        return merge(query(pool[x].l, a, m, l, r), query(pool[x].r, m + 1, b, l, r));
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE auto rangeSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        Agg res = query(root, lo, hi, l, r);
        return res.sm;
    }

    // O(logU) -- best sum of a non-empty prefix of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxPrefixSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("maxPrefixSum: needs lo <= l <= r <= hi");
        Agg res = query(root, lo, hi, l, r);
        return res.pre;
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        int x = find(i);
        return x ? T(pool[x].v.sm) : T(0);
    }

    // O(logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
