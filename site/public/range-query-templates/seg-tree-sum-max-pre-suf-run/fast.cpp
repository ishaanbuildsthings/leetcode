// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-max-pre-suf-run/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: getAll leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAll maxPrefixSum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeSum rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX sumAll
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostPrefixSumGtX: log(N)
//   leftmostPrefixSumGteX: log(N)
//   longestEqualRun: log(N)
//   maxPrefixSum: log(N)
//   maxSuffixSum: log(N)
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeMax: log(N)
//   rangeSum: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostSuffixSumGtX: log(N)
//   rightmostSuffixSumGteX: log(N)
//   sumAll: log(N)
//   maxAll: log(N)
//   build: N
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] mx[2*N] pre[2*N] suf[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N]
//   tags: none
//   other: none
//   note: leaves [n, 2n) hold each value's own aggregates

// Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
// its sum, its max, its best prefix sum, its best suffix sum, its first / last value and the equal runs at its ends
// and inside over its range. All indices 0-based, ranges inclusive [l, r]; searches return -1 when nothing qualifies.
// Leaves tree[n..2n); a node used by a query or update is a perfect subtree of 2^s leaves (s = its level); an update
// rewrites a leaf, then its ancestors.
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
struct SegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n, h;
    HotVector<S> sm;
    HotVector<T> mx;
    HotVector<S> pre;
    HotVector<S> suf;
    HotVector<T> fv;
    HotVector<T> lv;
    HotVector<int> pr;
    HotVector<int> sr;
    HotVector<int> br;

    // O(N) -- arr: the initial array (non-empty)
    explicit SegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        mx.assign(2 * n, T(0));
        pre.assign(2 * n, 0);
        suf.assign(2 * n, 0);
        fv.assign(2 * n, T(0));
        lv.assign(2 * n, T(0));
        pr.assign(2 * n, 0);
        sr.assign(2 * n, 0);
        br.assign(2 * n, 0);
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        for (int x = n - 1; x > 0; x--) {
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)
            pull(x, s);
        }
    }

    // O(N) -- the whole array
    LEETCODE_NO_SANITIZE vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t] > x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t] >= x ? 2 * t : 2 * t + 1;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] > S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] > S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostPrefixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostPrefixSumGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] >= S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] >= S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int longestEqualRun(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("longestEqualRun: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0], p = pr[t], q = sr[t], res = br[t], k = 1 << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {
            t = ns[i];
            int w = 1 << ls[i];
            bool j = last == fv[t];
            res = max({res, br[t], j ? q + pr[t] : 0});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }
        return res;
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S maxPrefixSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxPrefixSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S maxSuffixSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("maxSuffixSum: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- a[i] += v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN) -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN) -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        int p = i + n;
        return leaf(p);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        T res = numeric_limits<T>::lowest();
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = max(res, mx[lo++]);
            if (hi & 1) res = max(res, mx[--hi]);
        }
        return res;
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] > x)) continue;
            while (t < n) t = mx[2 * t + 1] > x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (!(mx[t] >= x)) continue;
            while (t < n) t = mx[2 * t + 1] >= x ? 2 * t + 1 : 2 * t;  // walk down the passing node
            return t - n;
        }
        return -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGtX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] > S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] > S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums); needs
    // 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostSuffixSumGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostSuffixSumGteX: needs 0 <= l <= r < n");
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] >= S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] >= S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mx[p] = v, pre[p] = S(v), suf[p] = S(v), fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1;
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = 2 * x, b = 2 * x + 1;
        pre[x] = max(pre[a], sm[a] + pre[b]);
        suf[x] = max(suf[b], sm[b] + suf[a]);
        sm[x] = sm[a] + sm[b];
        mx[x] = max(mx[a], mx[b]);
        int hl = 1 << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
    }

    LEETCODE_NO_SANITIZE void rebuild(int p) {  // recompute every ancestor of leaf p
        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);
    }

    LEETCODE_NO_SANITIZE int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }
};
