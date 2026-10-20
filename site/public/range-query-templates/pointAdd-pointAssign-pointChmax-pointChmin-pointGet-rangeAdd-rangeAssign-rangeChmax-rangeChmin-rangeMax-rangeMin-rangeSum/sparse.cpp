// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeMax-rangeMin-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U)*log(U) amortized
//   pointAssign: log(U)*log(U) amortized
//   pointChmax: log(U)*log(U) amortized
//   pointChmin: log(U)*log(U) amortized
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) amortized
//   rangeAssign: log(U)*log(U) amortized
//   rangeChmax: log(U)*log(U) amortized
//   rangeChmin: log(U)*log(U) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)] sz[4*log(U)]
//   tags: addMx[4*log(U)] addMn[4*log(U)] addOther[4*log(U)] hasAssign[4*log(U)] assignVal[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. One shared node pool, call resetPool() between test cases

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every
// SparseBeatsChminChmax<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with
// children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats: range chmin / chmax / add / assign, range sum / min / max, point ops.
// All indices 0-based, ranges inclusive [l, r]. Without rangeAdd everything is amortized O(log U); with it,
// O(log^2 U) amortized (proven tight). Each node keeps max / second max / count of max, the same for min, and three
// add tags (for the max group, the min group and everything else) plus an assign tag.
// Glue that one-sided beats does not need: a node with one distinct value has mx == mn, so applyAdd folds the three
// deltas into one (vMax + vMin - vOther); with exactly two distinct values mx2 == mn and mn2 == mx, so the second
// max moves with the MIN group and the second min with the MAX group.
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct SparseBeatsChminChmax {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2, addMx, addMn, addOther, assignVal;
        long long cntMx, cntMn, sz;
        S tot;
        bool hasAssign;
    };
    static inline vector<Node> t{Node{}};  // node 0 is a placeholder
    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    static inline vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBeatsChminChmax(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }

    // O(1) -- forget every node of every SparseBeatsChminChmax<T>; call between test cases, then build new trees
    static void resetPool() { t.resize(1); Lc.resize(1); Rc.resize(1); ln.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only touches the shared pool
        t.push_back(Node{0, NEG_INF, 0, POS_INF, 0, 0, 0, 0, k, k, k, S(0), false});
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
        nd.sz = a.sz + b.sz;
        nd.tot = a.tot + b.tot;
        if (a.mx > b.mx) nd.mx = a.mx, nd.cntMx = a.cntMx, nd.mx2 = max(a.mx2, b.mx);
        else if (a.mx < b.mx) nd.mx = b.mx, nd.cntMx = b.cntMx, nd.mx2 = max(b.mx2, a.mx);
        else nd.mx = a.mx, nd.cntMx = a.cntMx + b.cntMx, nd.mx2 = max(a.mx2, b.mx2);
        if (a.mn < b.mn) nd.mn = a.mn, nd.cntMn = a.cntMn, nd.mn2 = min(a.mn2, b.mn);
        else if (a.mn > b.mn) nd.mn = b.mn, nd.cntMn = b.cntMn, nd.mn2 = min(b.mn2, a.mn);
        else nd.mn = a.mn, nd.cntMn = a.cntMn + b.cntMn, nd.mn2 = min(a.mn2, b.mn2);
        nd.hasAssign = false;
        nd.addMx = nd.addMn = nd.addOther = 0;
    }

    void applyAdd(int i, T vMax, T vMin, T vOther) {
        Node& nd = t[i];
        if (nd.mx == nd.mn) {
            T d = vMax + vMin - vOther;
            nd.tot += S(d) * nd.sz;
            nd.mx += d, nd.mn = nd.mx;
            if (nd.hasAssign) nd.assignVal = nd.mx;
            else nd.addMx += d, nd.addMn += d, nd.addOther += d;
            return;
        }
        nd.tot += S(vMax) * nd.cntMx + S(vMin) * nd.cntMn + S(vOther) * (nd.sz - nd.cntMx - nd.cntMn);
        if (nd.mx2 != NEG_INF) nd.mx2 += nd.mx2 == nd.mn ? vMin : vOther;
        if (nd.mn2 != POS_INF) nd.mn2 += nd.mn2 == nd.mx ? vMax : vOther;
        nd.mx += vMax, nd.mn += vMin;
        nd.addMx += vMax, nd.addMn += vMin, nd.addOther += vOther;
    }

    void applyAssign(int i, T v) {
        Node& nd = t[i];
        nd.mx = nd.mn = v, nd.mx2 = NEG_INF, nd.mn2 = POS_INF;
        nd.cntMx = nd.cntMn = nd.sz;
        nd.tot = S(v) * nd.sz;
        nd.addMx = nd.addMn = nd.addOther = 0;
        nd.hasAssign = true, nd.assignVal = v;
    }

    void push(int i) {
        kids(i);
        Node& nd = t[i];
        if (nd.sz == 1) return;
        int l = Lc[i], r = Rc[i];
        if (nd.hasAssign) {
            applyAssign(l, nd.assignVal), applyAssign(r, nd.assignVal);
            nd.hasAssign = false;
            return;
        }
        T aMx = nd.addMx, aMn = nd.addMn, aO = nd.addOther;
        if (aMx == 0 && aMn == 0 && aO == 0) return;
        T mxc = max(t[l].mx, t[r].mx), mnc = min(t[l].mn, t[r].mn);
        applyAdd(l, t[l].mx == mxc ? aMx : aO, t[l].mn == mnc ? aMn : aO, aO);
        applyAdd(r, t[r].mx == mxc ? aMx : aO, t[r].mn == mnc ? aMn : aO, aO);
        nd.addMx = nd.addMn = nd.addOther = 0;
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyAdd(i, x - t[i].mx, 0, 0); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(Lc[i], tl, tm, ql, qr, x), chmin(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyAdd(i, 0, x - t[i].mn, 0); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmax(Lc[i], tl, tm, ql, qr, x), chmax(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, v, v, v); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        add(Lc[i], tl, tm, ql, qr, v), add(Rc[i], tm + 1, tr, ql, qr, v);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, v); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        assign(Lc[i], tl, tm, ql, qr, v), assign(Rc[i], tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return t[i].tot;
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return qsum(Lc[i], tl, tm, ql, qr) + qsum(Rc[i], tm + 1, tr, ql, qr);
    }

    T qmax(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(Lc[i], tl, tm, ql, qr), qmax(Rc[i], tm + 1, tr, ql, qr));
    }

    T qmin(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return min(qmin(Lc[i], tl, tm, ql, qr), qmin(Rc[i], tm + 1, tr, ql, qr));
    }

    // amortized O(logU), O(log^2 U) once rangeAdd is used -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(long long l, long long r, T x) { if (l <= r) chmin(root, lo, hi, l, r, x); }

    // amortized O(logU), O(log^2 U) once rangeAdd is used -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(long long l, long long r, T x) { if (l <= r) chmax(root, lo, hi, l, r, x); }

    // amortized O(log^2 U) -- a[i] += x for i in [l, r]
    void rangeAdd(long long l, long long r, T x) { if (l <= r) add(root, lo, hi, l, r, x); }

    // O(logU) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return l > r ? NEG_INF : qmax(root, lo, hi, l, r); }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return l > r ? POS_INF : qmin(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) { return rangeMax(i, i); }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { rangeChmin(i, i, v); }

    // a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }
};
