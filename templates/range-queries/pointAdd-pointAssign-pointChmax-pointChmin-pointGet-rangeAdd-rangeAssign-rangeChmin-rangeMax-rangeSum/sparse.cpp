// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmin-rangeMax-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U)*log(U) amortized
//   pointAssign: log(U)*log(U) amortized
//   pointChmax: log(U)*log(U) amortized
//   pointChmin: log(U)*log(U) amortized
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) amortized
//   rangeAssign: log(U)*log(U) amortized
//   rangeChmin: log(U)*log(U) amortized
//   rangeMax: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] tot[4*log(U)] sz[4*log(U)]
//   tags: addMx[4*log(U)] addOther[4*log(U)] hasAssign[4*log(U)] assignVal[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats, one side only: range rangeChmin / add / assign, range sum / rangeMax, point ops. 0-based, inclusive.
// Each node keeps its max (mx), strict second max (mx2) and how many times the max appears, plus two add tags: one for
// the max group and one for everything else. A rangeChmin with mx2 < x < mx only moves the max group, so it becomes
// an add on that group alone. Amortized O(log^2 U) with rangeAdd in the mix (O(log U) without).
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct SparseBeatsChmin {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::lowest();  // "no second max"
    struct Node {
        T mx, mx2, addMx, addOther, assignVal;
        long long cntMx, sz;
        S tot;
        bool hasAssign;
    };
    mutable vector<Node> t{Node{}};  // node 0 is a placeholder
    mutable vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    static bool better(T a, T b) { return a > b; }  // a is strictly more extreme than b

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBeatsChmin(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        t.push_back(Node{0, INF, 0, 0, 0, k, k, S(0), false});
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
        if (better(a.mx, b.mx)) nd.mx = a.mx, nd.cntMx = a.cntMx, nd.mx2 = better(a.mx2, b.mx) ? a.mx2 : b.mx;
        else if (better(b.mx, a.mx)) nd.mx = b.mx, nd.cntMx = b.cntMx, nd.mx2 = better(b.mx2, a.mx) ? b.mx2 : a.mx;
        else nd.mx = a.mx, nd.cntMx = a.cntMx + b.cntMx, nd.mx2 = better(a.mx2, b.mx2) ? a.mx2 : b.mx2;
        nd.hasAssign = false;
        nd.addMx = nd.addOther = 0;
    }

    void applyAdd(int i, T vMx, T vOther) {
        Node& nd = t[i];
        nd.tot += S(vMx) * nd.cntMx + S(vOther) * (nd.sz - nd.cntMx);
        if (nd.mx2 != INF) nd.mx2 += vOther;
        nd.mx += vMx;
        if (nd.hasAssign) nd.assignVal = nd.mx;
        else nd.addMx += vMx, nd.addOther += vOther;
    }

    void applyAssign(int i, T v) {
        Node& nd = t[i];
        nd.mx = v, nd.mx2 = INF, nd.cntMx = nd.sz;
        nd.tot = S(v) * nd.sz;
        nd.addMx = nd.addOther = 0;
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
        T aMx = nd.addMx, aO = nd.addOther;
        if (aMx == 0 && aO == 0) return;
        T c = better(t[l].mx, t[r].mx) ? t[l].mx : t[r].mx;
        applyAdd(l, t[l].mx == c ? aMx : aO, aO);
        applyAdd(r, t[r].mx == c ? aMx : aO, aO);
        nd.addMx = nd.addOther = 0;
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || !better(t[i].mx, x)) return;
        if (ql <= tl && tr <= qr && better(x, t[i].mx2)) { applyAdd(i, x - t[i].mx, 0); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(Lc[i], tl, tm, ql, qr, x), chmin(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, v, v); return; }
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

    T qext(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        T a = qext(Lc[i], tl, tm, ql, qr), b = qext(Rc[i], tm + 1, tr, ql, qr);
        return better(a, b) ? a : b;
    }

    // amortized O(log^2 U) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(long long l, long long r, T x) { if (l <= r) chmin(root, lo, hi, l, r, x); }

    // amortized O(log^2 U) -- a[i] += x for i in [l, r]
    void rangeAdd(long long l, long long r, T x) { if (l <= r) add(root, lo, hi, l, r, x); }

    // O(logU) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return l > r ? INF : qext(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) { return rangeMax(i, i); }

    // a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { rangeChmin(i, i, v); }

    // a[i] = max(a[i], v): the other side is not a beats op here, so it is a point assign
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }
};
