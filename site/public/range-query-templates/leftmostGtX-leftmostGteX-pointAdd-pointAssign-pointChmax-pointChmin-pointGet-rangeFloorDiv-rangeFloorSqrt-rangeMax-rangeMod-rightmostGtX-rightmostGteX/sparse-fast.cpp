// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMod-rightmostGtX-rightmostGteX/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMod
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeFloorDiv: log(U)*log(U) amortized
//   rangeFloorSqrt: log(U)*log(log(U)) amortized
//   rangeMax: log(U)
//   rangeMod: log(U)*log(U) amortized
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// "Shrink" segment tree: range mod / floor-div / floor-sqrt, range sum / max, point ops. 0-based, inclusive.
// No lazy tags: an update walks down to every leaf that will actually change, pruning any subtree whose max is
// below the op's cutoff. Each such leaf at least halves (mod, div) or square-roots, so each value can only be hit
// O(log U) (or O(log log U)) times between point assigns. Values must be >= 0.
// T: int, long long, ...
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
struct SparseShrinkTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    mutable vector<T> mx = vector<T>(1);
    mutable HotVector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable HotVector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseShrinkTree(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) {
        mx.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes);
    }

    // a fresh node: a block of k zeros
    LEETCODE_NO_SANITIZE int node(long long k) const {  // const: it only grows the (mutable) pool
        mx.push_back(0);
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    LEETCODE_NO_SANITIZE void kids(int i) const {
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }

    LEETCODE_NO_SANITIZE void pull(int i) { mx[i] = max(mx[Lc[i]], mx[Rc[i]]); }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    LEETCODE_NO_SANITIZE static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    // descend to the leaves that change; cutoff = smallest value the op can change
    template <class F>
    LEETCODE_NO_SANITIZE void shrink(int i, long long tl, long long tr, long long ql, long long qr, T cutoff,
        const F& op) {
        if (qr < tl || ql > tr || mx[i] < cutoff) return;
        if (tl == tr) { mx[i] = op(mx[i]); return; }
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        shrink(Lc[i], tl, tm, ql, qr, cutoff, op), shrink(Rc[i], tm + 1, tr, ql, qr, cutoff, op);
        pull(i);
    }

    LEETCODE_NO_SANITIZE void set(int i, long long tl, long long tr, long long p, T v) {
        if (tl == tr) { mx[i] = v; return; }
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        if (p <= tm) set(Lc[i], tl, tm, p, v);
        else set(Rc[i], tm + 1, tr, p, v);
        pull(i);
    }

    LEETCODE_NO_SANITIZE T qmax(int i, long long tl, long long tr, long long ql, long long qr) const {
        if (ql > tr || qr < tl) return numeric_limits<T>::lowest();
        if (ql <= tl && tr <= qr) return mx[i];
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(Lc[i], tl, tm, ql, qr), qmax(Rc[i], tm + 1, tr, ql, qr));
    }

    // amortized O(logU logU) -- a[i] %= x for i in [l, r]; prunes at max < x, where a % x == a; needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeMod(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMod: needs lo <= l <= r <= hi");
        if (l <= r && x >= 1) shrink(root, lo, hi, l, r, x, [x](T v) { return v % x; });
    }

    // amortized O(logU logU) -- a[i] /= x (floor) for i in [l, r]; requires x >= 2, prunes at max < 1; needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorDiv(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeFloorDiv: needs lo <= l <= r <= hi");
        if (l <= r && x >= 2) shrink(root, lo, hi, l, r, T(1), [x](T v) { return v / x; });
    }

    // amortized O(logU loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r]; 0 and 1 are fixed points; needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeFloorSqrt(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeFloorSqrt: needs lo <= l <= r <= hi");
        if (l <= r) shrink(root, lo, hi, l, r, T(2), isqrtT);
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return l > r ? numeric_limits<T>::lowest() : qmax(root, lo, hi, l, r);
    }

    // O(logU) -- a[i] = v, an overwrite that may raise the value; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        set(root, lo, hi, i, v);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return rangeMax(i, i);
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

    // O(logU) -- a[i] += delta (the result must stay >= 0); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }
};
