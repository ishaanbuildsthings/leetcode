// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/lazy-seg-tree-sum-min-npre-or-updates-assign/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll leftmostLtX leftmostLteX leftmostPrefixSumLtX leftmostPrefixSumLteX minAll minPrefixSum orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeMin rangeOrQuery rangeSum rightmostLtX rightmostLteX sumAll
// @data-structure-type: lazy-seg-tree
// @complexities:
//   getAll: N
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   leftmostPrefixSumLtX: log(N)
//   leftmostPrefixSumLteX: log(N)
//   minPrefixSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeAssign: log(N)
//   rangeMin: log(N)
//   rangeOrQuery: log(N)
//   rangeSum: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   sumAll: log(N)
//   minAll: log(N)
//   orAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mn[2*N] npre[2*N] orr[2*N]
//   tags: asg[1*N] hasAsg[1*N]
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates; tags live on the N internal nodes only

// Lazy segment tree with composable aggregates (2N iterative): range updates (rangeAssign) and range queries in
// O(logN); each node keeps its sum, its min, its min prefix sum, its OR over its range. All indices 0-based, ranges
// inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update
// is a perfect subtree of 2^s leaves (s = its level), and every internal node holds its pending tags ("applied here,
// not yet to my children"): an update pushes the tags on its two boundary leaf paths, tags the covering nodes, then
// rebuilds both paths, each node redoing its own pending tag.
// T: int, long long, ...; sums are kept in S (long long for small T).
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
struct LazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h;
    HotVector<S> sm;
    HotVector<T> mn;
    HotVector<S> npre;
    HotVector<T> orr;
    HotVector<T> asg;
    HotVector<char> hasAsg;

    // O(N) -- arr: the initial array (non-empty)
    explicit LazySegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        mn.assign(2 * n, T(0));
        npre.assign(2 * n, 0);
        orr.assign(2 * n, T(0));
        asg.assign(n, T(0));
        hasAsg.assign(n, 0);
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) {
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)
            pull(x, s);
        }
    }

    // O(N) -- the whole array, every pending tag pushed down on the way
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        for (int x = 1; x < n; x++) {  // (parents before children)
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;
            push(x, s);
        }
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            if (!(mn[t] < x)) continue;
            while (t < n) push(t, s--), t = mn[2 * t] < x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) push(t, s--), t = mn[2 * t] <= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] < x, or -1 (a walk pruned by min prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumLtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            if (acc + npre[t] < S(x)) {
                while (t < n) {
                    push(t, s--);
                    if (acc + npre[2 * t] < S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] <= x, or -1 (a walk pruned by min prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumLteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            if (acc + npre[t] <= S(x)) {
                while (t < n) {
                    push(t, s--);
                    if (acc + npre[2 * t] <= S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S minPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("minPrefixSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = npre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = min(res, acc + npre[ns[i]]), acc += sm[ns[i]];
        return res;
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

    // O(logN) -- a[i] = v for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(int l, int r, T v) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) applyAssign(lo, s, v), lo++;
            if (hi & 1) hi--, applyAssign(hi, s, v);
        }
        rebuild(l + n), rebuild(r + n);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        T res = numeric_limits<T>::max();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = min(res, mn[lo++]);
            if (hi & 1) res = min(res, mn[--hi]);
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

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        pushPath(l + n), pushPath(r + n);
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            if (!(mn[t] < x)) continue;
            while (t < n) push(t, s--), t = mn[2 * t + 1] < x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            if (!(mn[t] <= x)) continue;
            while (t < n) push(t, s--), t = mn[2 * t + 1] <= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mn[p] = v, npre[p] = S(v), orr[p] = v;
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x, int s) {  // recompute node x (level s) from its children, then redo its own pending tags
        int a = 2 * x, b = 2 * x + 1;
        npre[x] = min(npre[a], sm[a] + npre[b]);
        sm[x] = sm[a] + sm[b];
        mn[x] = min(mn[a], mn[b]);
        orr[x] = orr[a] | orr[b];
        if (hasAsg[x]) setAssign(x, s, asg[x]);
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {  // recompute every ancestor of leaf p
        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);
    }

    LEETCODE_NO_SANITIZE int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        pushPath(l + n), pushPath(r + n);
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }

    LEETCODE_NO_SANITIZE void setAssign(int x, int s, T v) {  // every value under node x becomes v
        int k = 1 << s;
        sm[x] = S(v) * k;
        mn[x] = v;
        orr[x] = v;
        npre[x] = v < T(0) ? S(v) * k : S(v);
    }

    LEETCODE_NO_SANITIZE void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        if (x < n) asg[x] = v, hasAsg[x] = 1;
    }

    LEETCODE_NO_SANITIZE void push(int x, int s) {  // hand node x's pending tags to its children
        int a = 2 * x, b = 2 * x + 1, c = s - 1;  // (their level)
        if (hasAsg[x]) applyAssign(a, c, asg[x]), applyAssign(b, c, asg[x]), hasAsg[x] = 0;
    }

    LEETCODE_NO_SANITIZE void pushPath(int p) {  // hand down every pending tag on the path from the root to leaf p
        for (int s = h; s > 0; s--) push(p >> s, s);
    }
};
