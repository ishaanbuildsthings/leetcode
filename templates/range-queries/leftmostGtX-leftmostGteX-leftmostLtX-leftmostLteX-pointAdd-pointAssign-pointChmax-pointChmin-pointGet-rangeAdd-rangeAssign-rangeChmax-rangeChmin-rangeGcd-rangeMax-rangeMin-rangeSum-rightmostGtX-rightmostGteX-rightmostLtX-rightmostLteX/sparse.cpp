// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeGcd-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeGcd rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)*log(U)*log(U) amortized ?
//   pointAssign: log(U)*log(U)*log(U) amortized ?
//   pointChmax: log(U)*log(U)*log(U) amortized ?
//   pointChmin: log(U)*log(U)*log(U) amortized ?
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U)*log(U) amortized ?
//   rangeAssign: log(U)*log(U)*log(U) amortized ?
//   rangeChmax: log(U)*log(U)*log(U) amortized ?
//   rangeChmin: log(U)*log(U)*log(U) amortized ?
//   rangeGcd: log(U)*log(U) ?
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)] diffGcd[4*log(U)]
//   tags: addTag[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats with range gcd: range chmin / chmax / add / assign, range sum / min / max / gcd, point ops.
// All indices 0-based, ranges inclusive [l, r]. Each node keeps max / second max / count, min / second min / count,
// the sum, and diffGcd = gcd of pairwise differences among the node's "middle" values (neither its max nor its min).
// Chmin / chmax only move the max / min group, and add shifts everything uniformly, so diffGcd never changes under
// a tag; the node gcd is gcd(diffGcd, mx2 - mx, mn2 - mn, mx). A node with mn == mx pushes down as an assign.
// T: int, long long, ...; sums accumulate in S (long long for small T). Gcds are of absolute values.
template <typename T>
struct SparseBeatsGcd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2, diffGcd, addTag;
        long long cntMx, cntMn;
        S tot;
    };
    mutable vector<Node> t{Node{}};  // node 0 is a placeholder
    mutable vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    static T absT(T x) { return x < 0 ? -x : x; }

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBeatsGcd(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        t.push_back(Node{0, NEG_INF, 0, POS_INF, 0, 0, k, k, S(0)});
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }

    void pull(int i) {
        Node& nd = t[i];
        const Node &a = t[Lc[i]], &b = t[Rc[i]];
        nd.tot = a.tot + b.tot;
        if (a.mx > b.mx) nd.mx = a.mx, nd.cntMx = a.cntMx, nd.mx2 = max(a.mx2, b.mx);
        else if (a.mx < b.mx) nd.mx = b.mx, nd.cntMx = b.cntMx, nd.mx2 = max(b.mx2, a.mx);
        else nd.mx = a.mx, nd.cntMx = a.cntMx + b.cntMx, nd.mx2 = max(a.mx2, b.mx2);
        if (a.mn < b.mn) nd.mn = a.mn, nd.cntMn = a.cntMn, nd.mn2 = min(a.mn2, b.mn);
        else if (a.mn > b.mn) nd.mn = b.mn, nd.cntMn = b.cntMn, nd.mn2 = min(b.mn2, a.mn);
        else nd.mn = a.mn, nd.cntMn = a.cntMn + b.cntMn, nd.mn2 = min(a.mn2, b.mn2);
        T g = std::gcd(a.diffGcd, b.diffGcd);
        bool hasL = a.mx2 != NEG_INF && a.mx2 != a.mn, hasR = b.mx2 != NEG_INF && b.mx2 != b.mn;
        if (hasL && hasR) g = std::gcd(g, absT(a.mx2 - b.mx2));
        bool haveAny = hasL || hasR;
        T any = hasL ? a.mx2 : hasR ? b.mx2 : T(0);
        for (T val : {a.mn, a.mx, b.mn, b.mx})
            if (val != nd.mn && val != nd.mx) {
                if (haveAny) g = std::gcd(g, absT(val - any));
                else any = val, haveAny = true;
            }
        nd.diffGcd = g;
        nd.addTag = 0;
    }

    void applyAssign(int i, long long sz, T v) { t[i] = Node{v, NEG_INF, v, POS_INF, 0, 0, sz, sz, S(v) * sz}; }

    void applyAdd(int i, long long sz, T v) {
        Node& nd = t[i];
        if (nd.mn == nd.mx) { applyAssign(i, sz, nd.mx + v); return; }
        nd.mx += v, nd.mn += v;
        if (nd.mx2 != NEG_INF) nd.mx2 += v;
        if (nd.mn2 != POS_INF) nd.mn2 += v;
        nd.tot += S(v) * sz;
        nd.addTag += v;  // diffGcd untouched: a uniform shift does not change any difference
    }

    void applyChmin(int i, long long sz, T v) {
        Node& nd = t[i];
        if (nd.mn >= v) { applyAssign(i, sz, v); return; }
        if (nd.mx > v) {
            if (nd.mn2 == nd.mx) nd.mn2 = v;
            nd.tot -= S(nd.mx - v) * nd.cntMx;
            nd.mx = v;
        }
    }

    void applyChmax(int i, long long sz, T v) {
        Node& nd = t[i];
        if (nd.mx <= v) { applyAssign(i, sz, v); return; }
        if (nd.mn < v) {
            if (nd.mx2 == nd.mn) nd.mx2 = v;
            nd.tot += S(v - nd.mn) * nd.cntMn;
            nd.mn = v;
        }
    }

    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2, lsz = tm - tl + 1, rsz = tr - tm, l = Lc[i], r = Rc[i];
        if (t[i].mn == t[i].mx) { applyAssign(l, lsz, t[i].mx), applyAssign(r, rsz, t[i].mx); return; }
        if (T a = t[i].addTag) applyAdd(l, lsz, a), applyAdd(r, rsz, a), t[i].addTag = 0;
        applyChmin(l, lsz, t[i].mx), applyChmin(r, rsz, t[i].mx);
        applyChmax(l, lsz, t[i].mn), applyChmax(r, rsz, t[i].mn);
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(Lc[i], tl, tm, ql, qr, x), chmin(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyChmax(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmax(Lc[i], tl, tm, ql, qr, x), chmax(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        add(Lc[i], tl, tm, ql, qr, v), add(Rc[i], tm + 1, tr, ql, qr, v);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        assign(Lc[i], tl, tm, ql, qr, v), assign(Rc[i], tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return t[i].tot;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return qsum(Lc[i], tl, tm, ql, qr) + qsum(Rc[i], tm + 1, tr, ql, qr);
    }

    T qmax(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(Lc[i], tl, tm, ql, qr), qmax(Rc[i], tm + 1, tr, ql, qr));
    }

    T qmin(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return min(qmin(Lc[i], tl, tm, ql, qr), qmin(Rc[i], tm + 1, tr, ql, qr));
    }

    T nodeGcd(int i) const {
        const Node& nd = t[i];
        T g = nd.diffGcd;
        if (nd.mx2 != NEG_INF) g = std::gcd(g, absT(nd.mx2 - nd.mx));
        if (nd.mn2 != POS_INF) g = std::gcd(g, absT(nd.mn2 - nd.mn));
        return std::gcd(g, absT(nd.mx));
    }

    T qgcd(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return nodeGcd(i);
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return std::gcd(qgcd(Lc[i], tl, tm, ql, qr), qgcd(Rc[i], tm + 1, tr, ql, qr));
    }

    // amortized O(log^2 U logU) -- a[i] = min(a[i], x) for i in [l, r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    void rangeChmin(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeChmin: needs lo <= l <= r <= hi");
        if (l <= r) chmin(root, lo, hi, l, r, x);
    }

    // amortized O(log^2 U logU) -- a[i] = max(a[i], x) for i in [l, r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    void rangeChmax(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeChmax: needs lo <= l <= r <= hi");
        if (l <= r) chmax(root, lo, hi, l, r, x);
    }

    // amortized O(log^2 U logU) -- a[i] += x for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAdd(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAdd: needs lo <= l <= r <= hi");
        if (l <= r) add(root, lo, hi, l, r, x);
    }

    // amortized O(log^2 U logU) -- a[i] = x for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAssign(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        if (l <= r) assign(root, lo, hi, l, r, x);
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        return l > r ? S(0) : qsum(root, lo, hi, l, r);
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return l > r ? NEG_INF : qmax(root, lo, hi, l, r);
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return l > r ? POS_INF : qmin(root, lo, hi, l, r);
    }

    // O(logU logU) -- gcd of |a[l]|, ..., |a[r]|; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeGcd(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeGcd: needs lo <= l <= r <= hi");
        return l > r ? T(0) : qgcd(root, lo, hi, l, r);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return rangeMax(i, i);
    }

    // a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        rangeAssign(i, i, v);
    }

    // a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        rangeChmax(i, i, v);
    }

    // a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        rangeChmin(i, i, v);
    }

    // a[i] += delta; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        rangeAdd(i, i, delta);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return t[i].mx > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return t[i].mx >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return t[i].mn < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return t[i].mn <= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return t[i].mx > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return t[i].mx >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return t[i].mn < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return t[i].mn <= x; });
        return res == NONE ? lo - 1 : res;
    }

    static constexpr long long NONE = LLONG_MIN;  // ("no index": any long long can be an index here)

    // the first index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long firstPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = firstPass(Lc[i], tl, tm, l, r, ok);
        return res != NONE ? res : firstPass(Rc[i], tm + 1, tr, l, r, ok);
    }

    // the last index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long lastPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = lastPass(Rc[i], tm + 1, tr, l, r, ok);
        return res != NONE ? res : lastPass(Lc[i], tl, tm, l, r, ok);
    }
};