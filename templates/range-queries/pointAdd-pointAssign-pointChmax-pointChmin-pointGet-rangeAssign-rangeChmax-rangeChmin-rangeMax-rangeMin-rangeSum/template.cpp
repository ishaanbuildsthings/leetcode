// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   rangeChmax: log(N) amortized
//   rangeChmin: log(N) amortized
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cntMx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N]
//   tags: none
//   other: none
//   note: no tag arrays: on push, children are clamped to the parent's max/min (the beats tag is implicit)
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Chmax-Assign-Sum-Min-Max-PointSet-Beats-LogN.cpp

// Segment tree beats without range add: range chmin / chmax / assign, range sum / min / max, point ops.
// All indices 0-based, ranges inclusive [l, r]. Amortized O(log N) for everything: chmin / chmax / assign apply one
// function to a covered node, which can glue distinct values together but never split them. No add tags are
// needed: a node's own mx / mn ARE its pending chmin / chmax, and mn == mx means a pending assign.
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct BeatsChminChmaxNoAdd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2;
        int cntMx, cntMn;
        S tot;
    };
    int n;
    vector<Node> t;

    // O(N)
    explicit BeatsChminChmaxNoAdd(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { t[i] = Node{a[tl], NEG_INF, a[tl], POS_INF, 1, 1, S(a[tl])}; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        Node& nd = t[i];
        const Node &a = t[2 * i], &b = t[2 * i + 1];
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

    void applyAssign(int i, T v, int sz) { t[i] = Node{v, NEG_INF, v, POS_INF, sz, sz, S(v) * sz}; }

    void push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2, l = 2 * i, r = l + 1;
        if (t[i].mn == t[i].mx) { applyAssign(l, t[i].mx, tm - tl + 1), applyAssign(r, t[i].mx, tr - tm); return; }
        applyChmin(l, t[i].mx), applyChmin(r, t[i].mx);
        applyChmax(l, t[i].mn), applyChmax(r, t[i].mn);
    }

    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyChmin(i, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyChmax(i, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void assign(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, v, tr - tl + 1); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        assign(2 * i, tl, tm, ql, qr, v), assign(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return t[i].tot;
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, ql, qr) + qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }

    T qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }

    T qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(qmin(2 * i, tl, tm, ql, qr), qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }

    // amortized O(logN) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }

    // amortized O(logN) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) { if (l <= r && n) chmax(1, 0, n - 1, l, r, x); }

    // amortized O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return l > r || !n ? NEG_INF : qmax(1, 0, n - 1, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return l > r || !n ? POS_INF : qmin(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMax(i, i); }

    // a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // a[i] += delta, as a point assign (there is no add tag)
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
