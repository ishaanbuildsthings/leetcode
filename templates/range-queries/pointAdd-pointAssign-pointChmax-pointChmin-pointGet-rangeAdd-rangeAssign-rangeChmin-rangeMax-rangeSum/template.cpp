// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log^2(N) amortized
//   pointAssign: log^2(N) amortized
//   pointChmax: log^2(N) amortized
//   pointChmin: log^2(N) amortized
//   pointGet: log(N)
//   rangeAdd: log^2(N) amortized
//   rangeAssign: log^2(N) amortized
//   rangeChmin: log^2(N) amortized
//   rangeMax: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cntMx[4*N] tot[4*N] sz[4*N]
//   tags: addMx[4*N] addOther[4*N] hasAssign[4*N] assignVal[4*N]
//   other: none
//   note: 4n slots per array; every node field and tag is its own flat list
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Add-Assign-Sum-Max-PointSet-Beats.cpp

// Segment tree beats, one side only: range rangeChmin / add / assign, range sum / rangeMax, point ops. 0-based, inclusive.
// Each node keeps its max (mx), strict second max (mx2) and how many times the max appears, plus two add tags: one for
// the max group and one for everything else. A rangeChmin with mx2 < x < mx only moves the max group, so it becomes
// an add on that group alone. Amortized O(log^2 N) with rangeAdd in the mix (O(log N) without).
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct BeatsChmin {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::lowest();  // "no second max"
    struct Node {
        T mx, mx2, addMx, addOther, assignVal;
        int cntMx, sz;
        S tot;
        bool hasAssign;
    };
    int n;
    vector<Node> t;

    static bool better(T a, T b) { return a > b; }  // a is strictly more extreme than b

    // O(N)
    explicit BeatsChmin(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { t[i] = Node{a[tl], INF, 0, 0, 0, 1, 1, S(a[tl]), false}; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        Node& nd = t[i];
        const Node &a = t[2 * i], &b = t[2 * i + 1];
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
        Node& nd = t[i];
        if (nd.sz == 1) return;
        int l = 2 * i, r = l + 1;
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

    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || !better(t[i].mx, x)) return;
        if (ql <= tl && tr <= qr && better(x, t[i].mx2)) { applyAdd(i, x - t[i].mx, 0); return; }
        push(i);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, v, v); return; }
        push(i);
        int tm = (tl + tr) / 2;
        add(2 * i, tl, tm, ql, qr, v), add(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    void assign(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, v); return; }
        push(i);
        int tm = (tl + tr) / 2;
        assign(2 * i, tl, tm, ql, qr, v), assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return t[i].tot;
        push(i);
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, ql, qr) + qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }

    T qext(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i);
        int tm = (tl + tr) / 2;
        T a = qext(2 * i, tl, tm, ql, qr), b = qext(2 * i + 1, tm + 1, tr, ql, qr);
        return better(a, b) ? a : b;
    }

    // amortized O(log^2 N) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { if (l <= r && n) add(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return l > r || !n ? INF : qext(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMax(i, i); }

    // a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // a[i] = max(a[i], v): the other side is not a beats op here, so it is a point assign
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
