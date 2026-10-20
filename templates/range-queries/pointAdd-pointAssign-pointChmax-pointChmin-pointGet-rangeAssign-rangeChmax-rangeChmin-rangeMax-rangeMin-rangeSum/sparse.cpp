// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeChmin-rangeMax-rangeMin-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAssign: log(U) amortized
//   rangeChmax: log(U) amortized
//   rangeChmin: log(U) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. One shared node pool, call resetPool() between test cases

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every
// SparseBeatsChminChmaxNoAdd<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with
// children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats without range add: range chmin / chmax / assign, range sum / min / max, point ops.
// All indices 0-based, ranges inclusive [l, r]. Amortized O(log N) for everything: chmin / chmax / assign apply one
// function to a covered node, which can glue distinct values together but never split them. No add tags are
// needed: a node's own mx / mn ARE its pending chmin / chmax, and mn == mx means a pending assign.
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct SparseBeatsChminChmaxNoAdd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2;
        long long cntMx, cntMn;
        S tot;
    };
    static inline vector<Node> t{Node{}};  // node 0 is a placeholder
    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    static inline vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBeatsChminChmaxNoAdd(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }

    // O(1) -- forget every node of every SparseBeatsChminChmaxNoAdd<T>; call between test cases, then build new trees
    static void resetPool() { t.resize(1); Lc.resize(1); Rc.resize(1); ln.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only touches the shared pool
        t.push_back(Node{0, NEG_INF, 0, POS_INF, k, k, S(0)});
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
    }

    void applyChmin(int i, T x) {
        Node& nd = t[i];
        if (x >= nd.mx) return;
        nd.tot -= S(nd.mx - x) * nd.cntMx;
        if (nd.mn == nd.mx) nd.mn = x;
        else if (nd.mn2 == nd.mx) nd.mn2 = x;
        nd.mx = x;
    }

    void applyChmax(int i, T x) {
        Node& nd = t[i];
        if (x <= nd.mn) return;
        nd.tot += S(x - nd.mn) * nd.cntMn;
        if (nd.mx == nd.mn) nd.mx = x;
        else if (nd.mx2 == nd.mn) nd.mx2 = x;
        nd.mn = x;
    }

    void applyAssign(int i, T v, long long sz) { t[i] = Node{v, NEG_INF, v, POS_INF, sz, sz, S(v) * sz}; }

    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2, l = Lc[i], r = Rc[i];
        if (t[i].mn == t[i].mx) { applyAssign(l, t[i].mx, tm - tl + 1), applyAssign(r, t[i].mx, tr - tm); return; }
        applyChmin(l, t[i].mx), applyChmin(r, t[i].mx);
        applyChmax(l, t[i].mn), applyChmax(r, t[i].mn);
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyChmin(i, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(Lc[i], tl, tm, ql, qr, x), chmin(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyChmax(i, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmax(Lc[i], tl, tm, ql, qr, x), chmax(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, v, tr - tl + 1); return; }
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

    // amortized O(logN) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(long long l, long long r, T x) { if (l <= r) chmin(root, lo, hi, l, r, x); }

    // amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(long long l, long long r, T x) { if (l <= r) chmax(root, lo, hi, l, r, x); }

    // amortized O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return l > r ? NEG_INF : qmax(root, lo, hi, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return l > r ? POS_INF : qmin(root, lo, hi, l, r); }

    // O(logN) -- a[i]
    T pointGet(long long i) { return rangeMax(i, i); }

    // a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { rangeChmin(i, i, v); }

    // a[i] += delta, as a point assign (there is no add tag)
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
