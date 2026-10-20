// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeMin-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeMin rangeSum
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
//   rangeMin: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mn[4*log(U)] mn2[4*log(U)] cntMn[4*log(U)] tot[4*log(U)] sz[4*log(U)]
//   tags: addMn[4*log(U)] addOther[4*log(U)] hasAssign[4*log(U)] assignVal[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. One shared node pool, call resetPool() between test cases

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every
// SparseBeatsChmax<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with
// children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats, one side only: range rangeChmax / add / assign, range sum / rangeMin, point ops. 0-based, inclusive.
// Each node keeps its min (mn), strict second min (mn2) and how many times the min appears, plus two add tags: one for
// the min group and one for everything else. A rangeChmax with mn < x < mn2 only moves the min group, so it becomes
// an add on that group alone. Amortized O(log^2 U) with rangeAdd in the mix (O(log U) without).
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct SparseBeatsChmax {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max();  // "no second min"
    struct Node {
        T mn, mn2, addMn, addOther, assignVal;
        long long cntMn, sz;
        S tot;
        bool hasAssign;
    };
    static inline vector<Node> t{Node{}};  // node 0 is a placeholder
    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    static inline vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    static bool better(T a, T b) { return a < b; }  // a is strictly more extreme than b

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBeatsChmax(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }

    // O(1) -- forget every node of every SparseBeatsChmax<T>; call between test cases, then build new trees
    static void resetPool() { t.resize(1); Lc.resize(1); Rc.resize(1); ln.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { t.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only touches the shared pool
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
        if (better(a.mn, b.mn)) nd.mn = a.mn, nd.cntMn = a.cntMn, nd.mn2 = better(a.mn2, b.mn) ? a.mn2 : b.mn;
        else if (better(b.mn, a.mn)) nd.mn = b.mn, nd.cntMn = b.cntMn, nd.mn2 = better(b.mn2, a.mn) ? b.mn2 : a.mn;
        else nd.mn = a.mn, nd.cntMn = a.cntMn + b.cntMn, nd.mn2 = better(a.mn2, b.mn2) ? a.mn2 : b.mn2;
        nd.hasAssign = false;
        nd.addMn = nd.addOther = 0;
    }

    void applyAdd(int i, T vMn, T vOther) {
        Node& nd = t[i];
        nd.tot += S(vMn) * nd.cntMn + S(vOther) * (nd.sz - nd.cntMn);
        if (nd.mn2 != INF) nd.mn2 += vOther;
        nd.mn += vMn;
        if (nd.hasAssign) nd.assignVal = nd.mn;
        else nd.addMn += vMn, nd.addOther += vOther;
    }

    void applyAssign(int i, T v) {
        Node& nd = t[i];
        nd.mn = v, nd.mn2 = INF, nd.cntMn = nd.sz;
        nd.tot = S(v) * nd.sz;
        nd.addMn = nd.addOther = 0;
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
        T aMn = nd.addMn, aO = nd.addOther;
        if (aMn == 0 && aO == 0) return;
        T c = better(t[l].mn, t[r].mn) ? t[l].mn : t[r].mn;
        applyAdd(l, t[l].mn == c ? aMn : aO, aO);
        applyAdd(r, t[r].mn == c ? aMn : aO, aO);
        nd.addMn = nd.addOther = 0;
    }

    void chmax(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || !better(t[i].mn, x)) return;
        if (ql <= tl && tr <= qr && better(x, t[i].mn2)) { applyAdd(i, x - t[i].mn, 0); return; }
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmax(Lc[i], tl, tm, ql, qr, x), chmax(Rc[i], tm + 1, tr, ql, qr, x);
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
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        T a = qext(Lc[i], tl, tm, ql, qr), b = qext(Rc[i], tm + 1, tr, ql, qr);
        return better(a, b) ? a : b;
    }

    // amortized O(log^2 U) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(long long l, long long r, T x) { if (l <= r) chmax(root, lo, hi, l, r, x); }

    // amortized O(log^2 U) -- a[i] += x for i in [l, r]
    void rangeAdd(long long l, long long r, T x) { if (l <= r) add(root, lo, hi, l, r, x); }

    // O(logU) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return l > r ? INF : qext(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) { return rangeMin(i, i); }

    // a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v): the other side is not a beats op here, so it is a point assign
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(long long i, T delta) { rangeAdd(i, i, delta); }
};
