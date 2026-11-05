// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-maxAltSubseqSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMod-rightmostGtX-rightmostGteX/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: leftmostGtX leftmostGteX maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMod rightmostGtX rightmostGteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   maxAltSubseqSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeFloorDiv: log(U)*log(U) amortized
//   rangeFloorSqrt: log(U)*log(log(U)) amortized
//   rangeMax: log(U)
//   rangeMod: log(U)*log(U) amortized
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: none
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates), amortized for the shrink walks; node data per field, children L / R

// Shrink segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeFloorDiv, rangeMod, rangeFloorSqrt) and range queries in O(logU), U =
// hi - lo + 1; each node keeps its max, its best alternating (+ - + ...) subsequence sum for each start / end sign
// over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U
// positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children
// are created on demand as blocks of zeros, right before anything descends past a node. mod / floor div / floor sqrt
// walk down every node whose max still changes.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseShrinkSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        T mx = T(0);
        int L = 0;
        int R = 0;
    };
    vector<Node> nd{Node{}};  // node 0: none; node 1 is the root

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseShrinkSegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
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
    long long leftmostGteX(long long l, long long r, T x) {
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

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs lo <= l <= r <= hi, else
    // throws out_of_range
    S maxAltSubseqSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxAltSubseqSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{nd[ns[0]].a00, nd[ns[0]].a01, nd[ns[0]].a10, nd[ns[0]].a11};
        for (int i = 1; i < c; i++) a = altJoin(a, {nd[ns[i]].a00, nd[ns[i]].a01, nd[ns[i]].a10, nd[ns[i]].a11});
        return max(a[0], a[1]);
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // amortized O(logU * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing); needs
    // lo <= l <= r <= hi, else throws out_of_range
    void rangeFloorDiv(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rangeFloorDiv: needs lo <= l <= r <= hi");
        if (x >= 2)
            update(1, D, first, l, r, [&](int t, int s, long long) {
                shrink(t, s, T(1), [x](T v) { return T(v / x); });
            });
    }

    // amortized O(logU * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0); needs
    // lo <= l <= r <= hi, else throws out_of_range
    void rangeFloorSqrt(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeFloorSqrt: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) {
            shrink(t, s, T(2), isqrtT);
        });
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::lowest();
        for (int i = 0; i < c; i++) res = max(res, nd[ns[i]].mx);
        return res;
    }

    // amortized O(logU * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1); needs lo <= l <= r <= hi, else
    // throws out_of_range
    void rangeMod(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMod: needs lo <= l <= r <= hi");
        if (x >= 1)
            update(1, D, first, l, r, [&](int t, int s, long long) {
                shrink(t, s, x, [x](T v) { return T(v % x); });
            });
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
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
    long long rightmostGteX(long long l, long long r, T x) {
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

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    int newZero(int s) {  // a new node: a block of 2^s zeros
        Node n;
        n.L = 0, n.R = 0, n.mx = T(0), n.a00 = S(0), n.a01 = s ? S(0) : NEG, n.a10 = s ? S(0) : NEG, n.a11 = S(0);
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
    }

    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    void update(int x, int s, long long tl, long long l, long long r, const F& f) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            f(x, s, tl);
            return;
        }
        kids(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) update(nd[x].L, s - 1, tl, l, r, f);
        if (r >= m) update(nd[x].R, s - 1, m, l, r, f);
        pull(x);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
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

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k]);
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrink(int x, int s, T lim, const F& f) {  // every value v >= lim under node x (level s) becomes f(v)
        if (nd[x].mx < lim) return;
        if (s == 0) { setLeaf(x, f(nd[x].mx)); return; }
        kids(x, s);
        shrink(nd[x].L, s - 1, lim, f), shrink(nd[x].R, s - 1, lim, f);
        pull(x);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].mx = v, nd[p].a00 = S(v), nd[p].a01 = NEG, nd[p].a10 = NEG, nd[p].a11 = -S(v);
    }

    T leaf(int p) const { return T(nd[p].mx); }  // the value at leaf p

    void pull(int x) {  // recompute node x from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].mx = max(nd[a].mx, nd[b].mx);
        array<S,
            4> c = altJoin({nd[a].a00, nd[a].a01, nd[a].a10, nd[a].a11}, {nd[b].a00, nd[b].a01, nd[b].a10, nd[b].a11});
        nd[x].a00 = c[0], nd[x].a01 = c[1], nd[x].a10 = c[2], nd[x].a11 = c[3];
    }
};
