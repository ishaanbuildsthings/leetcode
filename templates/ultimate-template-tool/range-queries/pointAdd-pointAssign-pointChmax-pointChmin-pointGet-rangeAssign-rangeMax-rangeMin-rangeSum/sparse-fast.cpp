// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeMax-rangeMin-rangeSum/sparse-fast.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeMax rangeMin rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] mx[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); queries create nothing. A node pool per tree (node 0 = all zeros)

// Range assign with range sum / min / max queries, plus point ops, over any index range [lo, hi] (huge or negative is
// fine); every position starts at 0. The tag is a pending assign. Updates push a node's tag into its children (creating
// them) before recursing past it; queries never push: they carry the ancestors' tags down and apply them to what they
// return, so they create no nodes. Sparse: nodes exist only where updates reached, in a pool the tree owns; node 0 is
// the all-zeros block (its sum, min and max are 0 at any length). T: int, long long, ...; sums are kept in S
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
struct SparseAssignSumMinMaxTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    struct Agg { S sm; T mn; T mx; };
    struct Tag { T asg; bool has; };
    static constexpr Tag ID = Tag{0, false};
    struct Node { Agg v; Tag t; int l, r; };
    HotVector<Node> pool{Node{Agg{}, ID, 0, 0}};  // node 0: all zeros, its children are itself
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseAssignSumMinMaxTree(long long lo, long long hi) : lo(lo), hi(hi) { root = make(); }


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

    LEETCODE_NO_SANITIZE static bool isId(const Tag& t) { return !t.has; }
    // tag o, then tag t
    LEETCODE_NO_SANITIZE static Tag compose(const Tag& o, const Tag& t) { return t.has ? t : o; }

    // the aggregate of k slots after tag t
    LEETCODE_NO_SANITIZE static Agg applyTag(Agg v, long long k, const Tag& t) {
        if (t.has) {
            v.sm = S(t.asg) * k;
            v.mn = t.asg;
            v.mx = t.asg;
        }
        return v;
    }

    LEETCODE_NO_SANITIZE static Agg merge(const Agg& a, const Agg& b) { return Agg{a.sm + b.sm, std::min(a.mn, b.mn), std::max(a.mx, b.mx)}; }

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

    LEETCODE_NO_SANITIZE void pull(int x, long long k) {
        Agg v = merge(pool[pool[x].l].v, pool[pool[x].r].v);
        pool[x].v = v;
        (void)k;
    }

    LEETCODE_NO_SANITIZE void update(int x, long long a, long long b, long long l, long long r, const Tag& t) {
        if (l <= a && b <= r) { applyNode(x, b - a + 1, t); return; }
        push(x, a, b);
        long long m = a + (b - a) / 2;
        if (l <= m) update(kid(x, false), a, m, l, r, t);
        if (r > m) update(kid(x, true), m + 1, b, l, r, t);
        pull(x, b - a + 1);
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

    // O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void rangeAssign(long long l, long long r, T v) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        if (l <= r) update(root, lo, hi, l, r, Tag{v, true});
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE S rangeSum(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        return query(root, lo, hi, l, r, ID).sm;
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMin(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return query(root, lo, hi, l, r, ID).mn;
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T rangeMax(long long l, long long r) const {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return query(root, lo, hi, l, r, ID).mx;
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE T pointGet(long long i) const {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return T(query(root, lo, hi, i, i, ID).sm);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    LEETCODE_NO_SANITIZE void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[130], d = 0, y = root;
        long long len[130], a = lo, b = hi;
        while (a < b) {
            push(y, a, b);
            path[d] = y, len[d++] = b - a + 1;
            long long m = a + (b - a) / 2;
            if (i <= m) y = kid(y, false), b = m;
            else y = kid(y, true), a = m + 1;
        }
        pool[y].v = Agg{S(v), v, v};
        while (d--) pull(path[d], len[d]);
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
