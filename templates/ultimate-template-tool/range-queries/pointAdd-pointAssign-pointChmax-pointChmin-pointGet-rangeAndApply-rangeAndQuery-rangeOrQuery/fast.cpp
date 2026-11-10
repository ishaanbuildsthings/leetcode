// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrQuery/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll getAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrQuery
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAndApply: log(N)
//   rangeAndQuery: log(N)
//   rangeOrQuery: log(N)
//   andAll: log(N)
//   orAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: an[2*N] orr[2*N]
//   tags: tA[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAndApply) and range queries in
// O(logN); each node keeps its AND, its OR over its range. All indices 0-based, ranges inclusive [l, r]; searches
// return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s
// leaves (s = its level), and every internal node holds its pending tags ("applied here, not yet to my children"): an
// update pushes the tags on its two boundary leaf paths, tags the covering nodes, then rebuilds both paths, each node
// redoing its own pending tag.
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
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const {
        return this->_M_impl._M_start[i];
    }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct LazySegTree {
    int n, h;
    HotVector<T> an;
    HotVector<T> orr;
    HotVector<T> tA;

    // O(N) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        an.assign(2 * n, ~T(0));
        orr.assign(2 * n, T(0));
        tA.assign(n, ~T(0));
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) pull(x);
    }

    // O(N) -- the whole array, every pending tag pushed down on the way
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) push(x);  // (parents before children)
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        pushPath(p);
        return leaf(p);
    }

    // O(logN) -- a[i] &= v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAndApply(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndApply: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) applyBits(lo, v), lo++;
            if (hi & 1) hi--, applyBits(hi, v);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        T res = ~T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res &= an[lo++];
            if (hi & 1) res &= an[--hi];
        }
        return res;
    }

    // O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res |= orr[lo++];
            if (hi & 1) res |= orr[--hi];
        }
        return res;
    }

    // O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        an[p] = v, orr[p] = v;
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(an[p]); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute node x from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        an[x] = an[a] & an[b];
        orr[x] = orr[a] | orr[b];
        if (tA[x] != ~T(0)) setBits(x, tA[x]);
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {  // recompute every ancestor of leaf p
        while (p > 1) p >>= 1, pull(p);
    }

    LEETCODE_NO_SANITIZE int cover(int l, int r, int* ns, int* ls) {
        // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        pushPath(l + n), pushPath(r + n);
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }

    LEETCODE_NO_SANITIZE void setBits(int x, T A) {  // every value v under node x becomes v & A
        an[x] = an[x] & A;
        orr[x] = orr[x] & A;
    }

    LEETCODE_NO_SANITIZE void applyBits(int x, T A) {
        setBits(x, A);
        if (x < n) tA[x] &= A;
    }

    LEETCODE_NO_SANITIZE void push(int x) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1;
        if (tA[x] != ~T(0)) {
            applyBits(a, tA[x]), applyBits(b, tA[x]);
            tA[x] = ~T(0);
        }
    }

    LEETCODE_NO_SANITIZE void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s);
    }
};
