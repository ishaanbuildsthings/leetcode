// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/longestEqualRun-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeSum/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: longestEqualRun pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   longestEqualRun: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeAssign: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)] add[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAdd, rangeAssign) and range queries in O(logU), U = hi - lo + 1; each
// node keeps its sum, its first / last value and the equal runs at its ends and inside over its range. Ranges
// inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the
// ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as
// blocks of zeros, right before anything descends past a node, and a node's pending tags ("applied here, not yet to
// my children") go down as it is passed.
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
#ifdef __GLIBCXX__
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::reference operator[](size_t i) { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE typename vector<U>::const_reference operator[](size_t i) const { return this->_M_impl._M_start[i]; }
    LEETCODE_NO_SANITIZE_INLINE size_t size() const { return size_t(this->_M_impl._M_finish - this->_M_impl._M_start); }
#endif
};

template <typename T>
struct SparseLazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S sm = 0;
        long long pr = 0;
        long long sr = 0;
        long long br = 0;
        T fv = T(0);
        T lv = T(0);
        T asg = T(0);
        T add = T(0);
        int L = 0;
        int R = 0;
        char hasAsg = 0;
    };
    HotVector<Node> nd{Node{}};  // node 0: none; node 1 is the root

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    LEETCODE_NO_SANITIZE long long longestEqualRun(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("longestEqualRun: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0];
        // (prefix run, suffix run, best, length)
        long long p = nd[t].pr, q = nd[t].sr, res = nd[t].br, k = 1LL << ls[0];
        T last = nd[t].lv;
        for (int i = 1; i < c; i++) {
            t = ns[i];
            long long w = 1LL << ls[i];
            bool j = last == nd[t].fv;
            res = max({res, nd[t].br, j ? q + nd[t].pr : 0LL});
            if (j && p == k) p += nd[t].pr;
            q = j && nd[t].sr == w ? q + nd[t].sr : nd[t].sr;
            k += w, last = nd[t].lv;
        }
        return res;
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

    // O(logU) -- a[i] += v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAdd(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAdd: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAdd(t, s, v); });
    }

    // O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += nd[ns[i]].sm;
        return res;
    }

    // ---- internals ----

    LEETCODE_NO_SANITIZE int newZero(int s) {  // a new node: a block of 2^s zeros
        Node n;
        n.L = 0, n.R = 0, n.sm = S(0), n.fv = T(0), n.lv = T(0), n.pr = 1LL << s, n.sr = 1LL << s, n.br = 1LL << s,
        n.asg = T(0), n.hasAsg = 0, n.add = T(0);
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
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    LEETCODE_NO_SANITIZE void update(int x, int s, long long tl, long long l, long long r, const F& f) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            f(x, s, tl);
            return;
        }
        kids(x, s);
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) update(nd[x].L, s - 1, tl, l, r, f);
        if (r >= m) update(nd[x].R, s - 1, m, l, r, f);
        pull(x, s);
    }

    LEETCODE_NO_SANITIZE int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            push(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    LEETCODE_NO_SANITIZE void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    LEETCODE_NO_SANITIZE void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].sm = S(v), nd[p].fv = v, nd[p].lv = v, nd[p].pr = 1, nd[p].sr = 1, nd[p].br = 1;
    }

    LEETCODE_NO_SANITIZE T leaf(int p) const { return T(nd[p].sm); }  // the value at leaf p

    LEETCODE_NO_SANITIZE void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].sm = nd[a].sm + nd[b].sm;
        long long hl = 1LL << (s - 1);
        bool j = nd[a].lv == nd[b].fv;
        nd[x].br = max({nd[a].br, nd[b].br, j ? nd[a].sr + nd[b].pr : 0LL});
        nd[x].pr = j && nd[a].pr == hl ? nd[a].pr + nd[b].pr : nd[a].pr;
        nd[x].sr = j && nd[b].sr == hl ? nd[b].sr + nd[a].sr : nd[b].sr;
        nd[x].fv = nd[a].fv, nd[x].lv = nd[b].lv;
    }

    LEETCODE_NO_SANITIZE void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        nd[x].sm = S(v) * k;
        nd[x].fv = nd[x].lv = v;
        nd[x].pr = nd[x].sr = nd[x].br = k;
    }

    LEETCODE_NO_SANITIZE void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        nd[x].asg = v, nd[x].hasAsg = 1, nd[x].add = T(0);
    }

    LEETCODE_NO_SANITIZE void setAdd(int x, int s, T v) {  // every value under node x gains v
        nd[x].sm += S(v) * (S(1) << s);
        nd[x].fv += v, nd[x].lv += v;
    }

    LEETCODE_NO_SANITIZE void applyAdd(int x, int s, T v) {
        setAdd(x, s, v);
        if (nd[x].hasAsg) nd[x].asg += v;  // (still an assign, of a shifted value)
        else nd[x].add += v;
    }

    LEETCODE_NO_SANITIZE void push(int x, int s) {  // hand node x's pending tags to its children
        int a = nd[x].L, b = nd[x].R, c = s - 1;  // (their level)
        if (nd[x].hasAsg) applyAssign(a, c, nd[x].asg), applyAssign(b, c, nd[x].asg), nd[x].hasAsg = 0;
        if (nd[x].add != T(0)) applyAdd(a, c, nd[x].add), applyAdd(b, c, nd[x].add), nd[x].add = T(0);
    }
};
