// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign
// @data-structure-type: seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: none
//   tags: stamp[4*log(U)] val[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes a range update visits (at most 4 per level), each remembering the newest assignment covering it. A node pool per tree

// Range assign + point ops over any index range [lo, hi] (huge or negative is fine); every position starts at 0. No
// pushing anywhere: assignments are stamped with an increasing counter, every node remembers the newest one covering
// it, and pointGet returns the newest on the leaf's root path. Sparse: nodes exist only where updates reached, in a
// pool the tree owns. T: int, long long, ...
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseRangeAssignTree {
    struct Node { int stamp; T v; int l, r; };  // the newest assignment covering the node (stamp 0: none)
    HotVector<Node> pool{Node{}};  // node 0 is never used: a 0 link means "not created yet"
    long long lo, hi;
    int root, clock = 0;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseRangeAssignTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{0, T(0), 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it if missing
    LEETCODE_NO_SANITIZE int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    LEETCODE_NO_SANITIZE void update(int x, long long a, long long b, long long l, long long r, int c, T v) {
        if (l <= a && b <= r) { pool[x].stamp = c, pool[x].v = v; return; }
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, c, v);
        if (r > m) update(kid(x, true), m + 1, b, l, r, c, v);
    }

    // O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(long long l, long long r, T v) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        if (l <= r) update(root, lo, hi, l, r, ++clock, v);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        int y = root, best = 0;
        T res = 0;
        long long a = lo, b = hi;
        while (y) {
            if (pool[y].stamp > best) best = pool[y].stamp, res = pool[y].v;
            if (a == b) break;
            long long m = a + (b - a) / 2;
            if (i <= m) y = pool[y].l, b = m;
            else y = pool[y].r, a = m + 1;
        }
        return res;
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int y = root;
        long long a = lo, b = hi;
        while (a < b) {
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].stamp = ++clock, pool[y].v = v;
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
