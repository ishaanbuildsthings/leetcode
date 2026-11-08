// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMax-rangeMin-rangeOrApply-rangeOrQuery-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: andAll getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxAll minAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMax rangeMin rangeOrApply rangeOrQuery rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   andAll: log(N)
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   maxAll: log(N)
//   minAll: log(N)
//   orAll: log(N)
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAndApply: log(N)*log(U) amortized
//   rangeAndQuery: log(N)
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeOrApply: log(N)*log(U) amortized
//   rangeOrQuery: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mn[4*N] andAgg[4*N] orAgg[4*N]
//   tags: tagAnd[4*N] tagXor[4*N]
//   other: none
//   note: the and/or tags compose into one (and, xor) pair per node (or X is the pair (~X, X)); no range xor, see BitCountTree
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-AndApply-OrApply-Min-Max-Sum-AndQuery-OrQuery-pointSet.cpp

// Bitwise segment tree beats: range and= / or=, range max / min / and / or, point ops.
// All indices 0-based, ranges inclusive. Values live in [0, 2^bits). Every update is the map v -> (v & a) ^ x:
//   and X -> (X, 0)   or X -> (~X, X)
// and those compose into one (and, xor) tag. A tag may only be applied to a whole node when every bit the node's
// values DISAGREE on is merely kept (mixed & (~a | x) == 0): then every value moves by the same delta, so max / min just shift.
// Otherwise recurse; each recursion makes a mixed bit uniform, which pays for it.
// No range xor: xor flips a mixed bit without making it uniform, so it could recurse to every leaf, O(N) per op.
// For xor with sums use BitCountTree (per-bit counts), which needs no beats at all.
// T: int, long long, ....
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
struct BitBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    T FULL;
    HotVector<T> mx, mn, andAgg, orAgg, tagAnd, tagXor;

    // O(N)
    explicit BitBeats(const vector<T>& a, int bits = 20)
        : n((int)a.size()), FULL(T((T(1) << bits) - 1)), mx(4 * max(1, n)), mn(4 * max(1, n)), andAgg(4 * max(1, n), FULL), orAgg(4 * max(1, n)), tagAnd(4 * max(1, n), FULL), tagXor(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    LEETCODE_NO_SANITIZE void setLeaf(int i, T v) {
        mx[i] = mn[i] = andAgg[i] = orAgg[i] = v;
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    LEETCODE_NO_SANITIZE void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { setLeaf(i, a[tl]); return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    LEETCODE_NO_SANITIZE void pull(int i) {
        int l = 2 * i, r = l + 1;
        mx[i] = max(mx[l], mx[r]);
        mn[i] = min(mn[l], mn[r]);
        andAgg[i] = andAgg[l] & andAgg[r], orAgg[i] = orAgg[l] | orAgg[r];
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // only legal when the node's mixed bits are all kept, so every value shifts by the same delta
    LEETCODE_NO_SANITIZE void apply(int i, T a, T x) {
        T keep = (a ^ x) & FULL;
        T delta = (~orAgg[i] & x & FULL) - (andAgg[i] & ~keep & FULL);
        mx[i] += delta, mn[i] += delta;
        andAgg[i] = ((andAgg[i] & a) ^ x) & FULL, orAgg[i] = ((orAgg[i] & a) ^ x) & FULL;
        tagAnd[i] = tagAnd[i] & a & FULL, tagXor[i] = ((tagXor[i] & a) ^ x) & FULL;
    }

    LEETCODE_NO_SANITIZE void push(int i, int tl, int tr) {
        if (tl == tr || (tagAnd[i] == FULL && tagXor[i] == 0)) return;
        apply(2 * i, tagAnd[i], tagXor[i]), apply(2 * i + 1, tagAnd[i], tagXor[i]);
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // (v & a) ^ x == v for every v in the node? keep bits are fine, flip bits never are, force-0 needs all 0,
    // force-1 needs all 1
    LEETCODE_NO_SANITIZE bool noEffect(int i, T a, T x) const {
        if (a & x & FULL) return false;
        if (~a & ~x & orAgg[i] & FULL) return false;
        if (~a & x & ~andAgg[i] & FULL) return false;
        return true;
    }

    LEETCODE_NO_SANITIZE void upd(int i, int tl, int tr, int ql, int qr, T a, T x) {
        if (qr < tl || ql > tr || noEffect(i, a, x)) return;
        T mixed = (andAgg[i] ^ orAgg[i]) & FULL;
        if (ql <= tl && tr <= qr && (mixed & (~a | x) & FULL) == 0) { apply(i, a, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        upd(2 * i, tl, tm, ql, qr, a, x), upd(2 * i + 1, tm + 1, tr, ql, qr, a, x);
        pull(i);
    }

    LEETCODE_NO_SANITIZE void set(int i, int tl, int tr, int p, T v) {
        if (tl == tr) { setLeaf(i, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        if (p <= tm) set(2 * i, tl, tm, p, v);
        else set(2 * i + 1, tm + 1, tr, p, v);
        pull(i);
    }

    // kind: 0 max, 1 min, 2 and, 3 or; identities are valid because every value is in [0, FULL]
    LEETCODE_NO_SANITIZE S query(int i, int tl, int tr, int ql, int qr, int kind) {
        if (qr < tl || ql > tr) {
            switch (kind) {
                case 0: return S(0);
                case 1: return S(FULL);
                case 2: return S(FULL);
                default: return S(0);
            }
        }
        if (ql <= tl && tr <= qr) {
            switch (kind) {
                case 0: return mx[i];
                case 1: return mn[i];
                case 2: return andAgg[i];
                default: return orAgg[i];
            }
        }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        S a = query(2 * i, tl, tm, ql, qr, kind), b = query(2 * i + 1, tm + 1, tr, ql, qr, kind);
        switch (kind) {
            case 0: return max(a, b);
            case 1: return min(a, b);
            case 2: return a & b;
            default: return a | b;
        }
    }

    // amortized O(logN logU) -- a[i] &= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAndApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndApply: needs 0 <= l <= r < n");
        if (l <= r && n) upd(1, 0, n - 1, l, r, X & FULL, 0);
    }

    // amortized O(logN logU) -- a[i] |= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeOrApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrApply: needs 0 <= l <= r < n");
        if (l <= r && n) upd(1, 0, n - 1, l, r, ~X & FULL, X & FULL);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return T(query(1, 0, n - 1, l, r, 0));
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return T(query(1, 0, n - 1, l, r, 1));
    }

    // O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        return l > r || !n ? FULL : T(query(1, 0, n - 1, l, r, 2));
    }

    // O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        return l > r || !n ? T(0) : T(query(1, 0, n - 1, l, r, 3));
    }

    // O(logN) -- a[i] = v & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        if (n) set(1, 0, n - 1, i, v & FULL);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return rangeAndQuery(i, i);
    }

    LEETCODE_NO_SANITIZE void getAllRec(int i, int tl, int tr, vector<T>& out) {
        if (tl == tr) { out.push_back(andAgg[i]); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        getAllRec(2 * i, tl, tm, out), getAllRec(2 * i + 1, tm + 1, tr, out);
    }

    // O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    LEETCODE_NO_SANITIZE vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        if (n) getAllRec(1, 0, n - 1, out);
        return out;
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

    // O(logN) -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    LEETCODE_NO_SANITIZE auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
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

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] > x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] >= x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] < x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] <= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] > x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] >= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] < x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    LEETCODE_NO_SANITIZE int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] <= x; });
    }

    // the first index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    LEETCODE_NO_SANITIZE int firstPass(int i, int tl, int tr, int l, int r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return -1;
        if (tl == tr) return tl;
        push(i, tl, tr);
        int tm = (tl + tr) / 2, res = firstPass(2 * i, tl, tm, l, r, ok);
        return res != -1 ? res : firstPass(2 * i + 1, tm + 1, tr, l, r, ok);
    }

    // the last index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    LEETCODE_NO_SANITIZE int lastPass(int i, int tl, int tr, int l, int r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return -1;
        if (tl == tr) return tl;
        push(i, tl, tr);
        int tm = (tl + tr) / 2, res = lastPass(2 * i + 1, tm + 1, tr, l, r, ok);
        return res != -1 ? res : lastPass(2 * i, tl, tm, l, r, ok);
    }
};
