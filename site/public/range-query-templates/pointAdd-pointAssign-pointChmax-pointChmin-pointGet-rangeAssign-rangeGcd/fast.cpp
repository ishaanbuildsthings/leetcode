// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeGcd/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: log(N)
//   rangeAssign: log(N)*log(U) ?
//   rangeGcd: log(N)+log(U) ?
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: t[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: leaves t[n..2n) hold the values, internal nodes the gcd of |values| below; tags live on internal nodes only

// Range assign + range gcd, plus point ops. All indices 0-based, ranges inclusive [l, r]. Gcds are of |values|.
// Iterative 2N lazy tree: leaves hold the values, internal nodes the gcd below them, and a pending assign on each
// internal node ("applied here, not yet pushed"). A node assigned v has gcd |v|, so assign is an ordinary lazy tag.
// Much lighter than the gcd beats tree when you only need assign. T: int, long long, ...
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
struct AssignGcdTree {
    int n, h;
    HotVector<T> t, asg;  // t: 2N (leaves = values, internal = gcd); asg: N tags on internal nodes
    HotVector<char> hasAsg;

    LEETCODE_NO_SANITIZE static T absT(T x) { return x < 0 ? -x : x; }

    // O(N logU)
    explicit AssignGcdTree(const vector<T>& a)
        : n((int)a.size()), h(a.empty() ? 0 : 32 - __builtin_clz((unsigned)a.size())), t(2 * a.size()), asg(a.size()), hasAsg(a.size()) {
        for (int i = 0; i < n; i++) t[n + i] = a[i];
        for (int x = n - 1; x > 0; x--) t[x] = std::gcd(absT(t[2 * x]), absT(t[2 * x + 1]));
    }

    LEETCODE_NO_SANITIZE void apply(int x, T v) {
        if (x < n) t[x] = absT(v), hasAsg[x] = 1, asg[x] = v;
        else t[x] = v;
    }

    LEETCODE_NO_SANITIZE void push(int p) {
        for (int s = h; s > 0; s--) {
            int x = p >> s;
            if (hasAsg[x]) apply(2 * x, asg[x]), apply(2 * x + 1, asg[x]), hasAsg[x] = 0;
        }
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {
        for (p >>= 1; p; p >>= 1) t[p] = hasAsg[p] ? absT(asg[p]) : std::gcd(absT(t[2 * p]), absT(t[2 * p + 1]));
    }

    // O(logN logU) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        if (l > r) return;
        int l0 = l + n, r0 = r + n;
        push(l0), push(r0);
        for (int i = l0, j = r0 + 1; i < j; i >>= 1, j >>= 1) {
            if (i & 1) apply(i++, v);
            if (j & 1) apply(--j, v);
        }
        rebuild(l0), rebuild(r0);
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]| (the gcds telescope, so the fold costs one log U); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        if (l > r) return 0;
        l += n, r += n;
        push(l), push(r);
        T res = 0;
        for (r++; l < r; l >>= 1, r >>= 1) {
            if (l & 1) res = std::gcd(res, absT(t[l++]));
            if (r & 1) res = std::gcd(res, absT(t[--r]));
        }
        return res;
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        push(i + n);
        return t[i + n];
    }

    // O(N) -- the whole array: push every tag down (a parent's index is below its children's, so in index order
    // each node's tag is complete when it is pushed), then read the leaves
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++)
            if (hasAsg[x]) apply(2 * x, asg[x]), apply(2 * x + 1, asg[x]), hasAsg[x] = 0;
        return vector<T>(t.begin() + n, t.end());
    }

    // O(logN logU) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(logN logU) -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAssign(i, i, pointGet(i) + delta);
    }

    // O(logN logU) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) rangeAssign(i, i, v);
    }

    // O(logN logU) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) rangeAssign(i, i, v);
    }
};
