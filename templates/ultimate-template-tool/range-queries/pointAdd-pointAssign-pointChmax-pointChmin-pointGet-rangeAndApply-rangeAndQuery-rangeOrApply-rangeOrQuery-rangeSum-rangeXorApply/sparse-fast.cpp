// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum-rangeXorApply/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum rangeXorApply
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)*log(U)
//   pointAssign: log(U)*log(U)
//   pointChmax: log(U)*log(U)
//   pointChmin: log(U)*log(U)
//   pointGet: log(U)*log(U)
//   rangeAndApply: log(U)*log(U)
//   rangeAndQuery: log(U)*log(U)
//   rangeOrApply: log(U)*log(U)
//   rangeOrQuery: log(U)*log(U)
//   rangeSum: log(U)*log(U)
//   rangeXorApply: log(U)*log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: cnt[4*log(U)*log(U)]
//   tags: a[4*log(U)] x[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. every node keeps BITS counts (BITS = 20, the second log); a node pool per tree (node 0 = all zeros)

// Range and= / or= / xor= with range sum / and / or queries, plus point ops. Values live in [0, 2^BITS). Each node
// counts, for every bit, how many of its values have that bit set. Every update is a bit map v -> (v & a) ^ x, and per
// bit that is keep, force 0 (count = 0), force 1, or flip (count = length - count), so every update is an ordinary lazy
// tag. Sum = sum over bits of count * 2^bit. Over any index range [lo, hi] (huge or negative is fine); every position
// starts at 0. Updates push a node's tag into its children (creating them) before recursing past it; queries never
// push: they carry the ancestors' tags down and apply them to what they return, so they create no nodes. Sparse: nodes
// exist only where updates reached, in a pool the tree owns; node 0 is the all-zeros block. T: int, long long, ...
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
struct SparseBitCountTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr int BITS = 20;  // values live in [0, 2^BITS)
    static constexpr T FULL = T((T(1) << BITS) - 1);
    struct Agg { array<long long, BITS> c; };  // c[b] = how many values below have bit b set
    struct Tag { T a, x; };  // v -> (v & a) ^ x
    static constexpr Tag ID = Tag{FULL, 0};
    struct Node { Agg v; Tag t; int l, r; };
    HotVector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBitCountTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }


    // optional -- reserve room for this many nodes up front
    LEETCODE_NO_SANITIZE void reservePool(size_t nodes) { pool.reserve(nodes); }

    LEETCODE_NO_SANITIZE int make() {
        pool.push_back(Node{Agg{}, ID, 0, 0});
        return (int)pool.size() - 1;
    }

    // child of x, creating it (as a block of zeros) if missing
    LEETCODE_NO_SANITIZE int kid(int x, bool right) {
        int y = right ? pool[x].r : pool[x].l;
        if (!y) {
            y = make();
            (right ? pool[x].r : pool[x].l) = y;
        }
        return y;
    }

    LEETCODE_NO_SANITIZE static bool isId(const Tag& t) { return t.a == FULL && t.x == 0; }

    // tag o, then tag t
    LEETCODE_NO_SANITIZE static Tag compose(const Tag& o,
        const Tag& t) { return Tag{T(o.a & t.a), T((o.x & t.a) ^ t.x)}; }

    // the aggregate of k slots after tag t
    LEETCODE_NO_SANITIZE static Agg applyTag(Agg v, long long k, const Tag& t) {
        for (int b = 0; b < BITS; b++) {
            if (!(t.a >> b & 1)) v.c[b] = 0;
            if (t.x >> b & 1) v.c[b] = k - v.c[b];
        }
        return v;
    }

    // node x (k slots) takes tag t: its aggregate now, its children later
    LEETCODE_NO_SANITIZE void applyNode(int x, long long k, const Tag& t) {
        pool[x].v = applyTag(pool[x].v, k, t);
        pool[x].t = compose(pool[x].t, t);
    }

    // move x's tag (x covers [a, b]) into its children, creating them
    LEETCODE_NO_SANITIZE void push(int x, long long a, long long b) {
        if (isId(pool[x].t)) return;
        Tag t = pool[x].t;
        long long m = a + (b - a) / 2;
        applyNode(kid(x, false), m - a + 1, t);
        applyNode(kid(x, true), b - m, t);
        pool[x].t = ID;
    }

    LEETCODE_NO_SANITIZE void pull(int x) { pool[x].v = merge(pool[pool[x].l].v, pool[pool[x].r].v); }

    LEETCODE_NO_SANITIZE static Agg merge(const Agg& a, const Agg& b) {
        Agg r; for (int j = 0; j < BITS; j++) r.c[j] = a.c[j] + b.c[j]; return r;
    }

    LEETCODE_NO_SANITIZE void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {
        if (l <= a && b <= r) { applyNode(x, b - a + 1, t); return; }
        push(x, a, b);
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
        pull(x);
    }

    // aggregate of a[max(l, a)..min(r, b)] under node x (covering [a, b]), with t, the ancestors' pending tags, on top
    LEETCODE_NO_SANITIZE Agg query(int x, long long a, long long b, long long l, long long r, const Tag& t) const {
        if (!x) return applyTag(Agg{}, std::min(r, b) - std::max(l, a) + 1, t);
        if (l <= a && b <= r) return applyTag(pool[x].v, b - a + 1, t);
        Tag down = compose(pool[x].t, t);
        long long m = a + (b - a) / 2;
        if (r <= m) return query(pool[x].l, a, m, l, r, down);
        if (l > m) return query(pool[x].r, m + 1, b, l, r, down);
        return merge(query(pool[x].l, a, m, l, r, down), query(pool[x].r, m + 1, b, l, r, down));
    }

    // O(logU * logU) -- a[i] &= X for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAndApply(long long l, long long r, T X) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAndApply: needs lo <= l <= r <= hi");
        if (l <= r) update(root, lo, hi, l, r, Tag{T(X & FULL), 0});
    }

    // O(logU * logU) -- a[i] |= X for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeOrApply(long long l, long long r, T X) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeOrApply: needs lo <= l <= r <= hi");
        if (l <= r) update(root, lo, hi, l, r, Tag{T(~X & FULL), T(X & FULL)});
    }

    // O(logU * logU) -- a[i] ^= X for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeXorApply(long long l, long long r, T X) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeXorApply: needs lo <= l <= r <= hi");
        if (l <= r) update(root, lo, hi, l, r, Tag{FULL, T(X & FULL)});
    }

    // O(logU * logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        Agg res = query(root, lo, hi, l, r, ID);
        return [&] { S s = 0; for (int b = 0; b < BITS; b++) s += S(res.c[b]) << b; return s; }();
    }

    // O(logU * logU) -- a[l] & ... & a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeAndQuery(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAndQuery: needs lo <= l <= r <= hi");
        Agg res = query(root, lo, hi, l, r, ID);
        return [&] { T v = 0; for (int b = 0; b < BITS; b++) if (res.c[b] == r - l + 1) v |= T(1) << b; return v; }();
    }

    // O(logU * logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeOrQuery(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        Agg res = query(root, lo, hi, l, r, ID);
        return [&] { T v = 0; for (int b = 0; b < BITS; b++) if (res.c[b]) v |= T(1) << b; return v; }();
    }

    // O(logU * logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        Agg res = query(root, lo, hi, i, i, ID);
        return [&] { T v = 0; for (int b = 0; b < BITS; b++) v |= T(res.c[b]) << b; return v; }();
    }

    // O(logU * logU) -- a[i] = v & FULL; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[130], d = 0, y = root;
        long long a = lo, b = hi;
        while (a < b) {
            push(y, a, b);
            path[d++] = y;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].v = [&] { Agg r{}; v &= FULL; for (int b = 0; b < BITS; b++) r.c[b] = v >> b & 1; return r; }();
        while (d--) pull(path[d]);
    }

    // O(logU * logU) -- a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }
};
