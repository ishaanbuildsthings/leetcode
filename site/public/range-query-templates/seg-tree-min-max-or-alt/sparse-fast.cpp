// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/seg-tree-min-max-or-alt/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet rangeMax rangeMin rangeOrQuery rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: seg-tree
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   maxAltSubseqSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeOrQuery: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[4*log(U)] mx[4*log(U)] orr[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its min, its
// max, its OR, its best alternating (+ - + ...) subsequence sum for each start / end sign over its range. Ranges
// inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the
// ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as
// blocks of zeros, right before anything descends past a node.
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
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        T mn = T(0);
        T mx = T(0);
        T orr = T(0);
        int L = 0;
        int R = 0;
    };
    HotVector<Node> nd{Node{}};  // node 0: none; node 1 is the root

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mx > x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mx >= x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn < x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long leftmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].L].mn <= x) t = nd[t].L;
                else t = nd[t].R, tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs lo <= l <= r <= hi, else
    // throws out_of_range
    LEETCODE_NO_SANITIZE S maxAltSubseqSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxAltSubseqSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{nd[ns[0]].a00, nd[ns[0]].a01, nd[ns[0]].a10, nd[ns[0]].a11};
        for (int i = 1; i < c; i++) a = altJoin(a, {nd[ns[i]].a00, nd[ns[i]].a01, nd[ns[i]].a10, nd[ns[i]].a11});
        return max(a[0], a[1]);
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::lowest();
        for (int i = 0; i < c; i++) res = max(res, nd[ns[i]].mx);
        return res;
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, nd[ns[i]].mn);
        return res;
    }

    // O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res |= nd[ns[i]].orr;
        return res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mx > x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mx >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mx >= x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn < x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE long long rightmostLteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(nd[t].mn <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (nd[nd[t].R].mn <= x) t = nd[t].R, tl += 1LL << s;
                else t = nd[t].L;
            }
            return tl;
        }
        return first - 1;
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    LEETCODE_NO_SANITIZE static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    LEETCODE_NO_SANITIZE int newZero(int s) {  // a new node: a block of 2^s zeros
        Node n;
        n.L = 0, n.R = 0, n.mn = T(0), n.mx = T(0), n.orr = T(0), n.a00 = S(0), n.a01 = s ? S(0) : NEG,
        n.a10 = s ? S(0) : NEG, n.a11 = S(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    LEETCODE_NO_SANITIZE void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    LEETCODE_NO_SANITIZE int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    LEETCODE_NO_SANITIZE int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    LEETCODE_NO_SANITIZE void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    LEETCODE_NO_SANITIZE int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    LEETCODE_NO_SANITIZE void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k]);
    }

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].mn = v, nd[p].mx = v, nd[p].orr = v, nd[p].a00 = S(v), nd[p].a01 = NEG, nd[p].a10 = NEG,
            nd[p].a11 = -S(v);
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(nd[p].mn); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x) {  // recompute node x from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].mn = min(nd[a].mn, nd[b].mn);
        nd[x].mx = max(nd[a].mx, nd[b].mx);
        nd[x].orr = nd[a].orr | nd[b].orr;
        array<S,
            4> c = altJoin({nd[a].a00, nd[a].a01, nd[a].a10, nd[a].a11}, {nd[b].a00, nd[b].a01, nd[b].a10, nd[b].a11});
        nd[x].a00 = c[0], nd[x].a01 = c[1], nd[x].a10 = c[2], nd[x].a11 = c[3];
    }
};
