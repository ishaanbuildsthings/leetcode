// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log^2(N) amortized
//   pointAssign: log^2(N) amortized
//   pointChmax: log^2(N) amortized
//   pointChmin: log^2(N) amortized
//   pointGet: log(N)
//   rangeAdd: log^2(N) amortized
//   rangeAssign: log^2(N) amortized
//   rangeChmax: log^2(N) amortized
//   rangeChmin: log^2(N) amortized
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cntMx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N] sz[4*N]
//   tags: addMx[4*N] addMn[4*N] addOther[4*N] hasAssign[4*N] assignVal[4*N]
//   other: none
//   note: 4n slots per array; every node field and tag is its own flat list
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Chmax-Add-Assign-Sum-Min-Max-PointSet-Beats-Log2NAdd.cpp

// Segment tree beats: range chmin / chmax / add / assign, range sum / min / max, point ops.
// All indices 0-based, ranges inclusive [l, r]. Without rangeAdd everything is amortized O(log N); with it,
// O(log^2 N) amortized (proven tight). Each node keeps max / second max / count of max, the same for min, and three
// add tags (for the max group, the min group and everything else) plus an assign tag.
// Glue that one-sided beats does not need: a node with one distinct value has mx == mn, so applyAdd folds the three
// deltas into one (vMax + vMin - vOther); with exactly two distinct values mx2 == mn and mn2 == mx, so the second
// max moves with the MIN group and the second min with the MAX group.
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct BeatsChminChmax {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2, addMx, addMn, addOther, assignVal;
        int cntMx, cntMn, sz;
        S tot;
        bool hasAssign;
    };
    int n;
    vector<Node> t;

    // O(N)
    explicit BeatsChminChmax(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) {
            T v = a[tl];
            t[i] = Node{v, NEG_INF, v, POS_INF, 0, 0, 0, 0, 1, 1, 1, S(v), false};
            return;
        }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        Node& nd = t[i];
        const Node &a = t[2 * i], &b = t[2 * i + 1];
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
        Node& nd = t[i];
        if (nd.sz == 1) return;
        int l = 2 * i, r = l + 1;
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

    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyAdd(i, x - t[i].mx, 0, 0); return; }
        push(i);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyAdd(i, 0, x - t[i].mn, 0); return; }
        push(i);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, v, v, v); return; }
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

    T qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return t[i].mx;
        push(i);
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }

    T qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i);
        int tm = (tl + tr) / 2;
        return min(qmin(2 * i, tl, tm, ql, qr), qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }

    // amortized O(logN), O(log^2 N) once rangeAdd is used -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }

    // amortized O(logN), O(log^2 N) once rangeAdd is used -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) { if (l <= r && n) chmax(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { if (l <= r && n) add(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return l > r || !n ? NEG_INF : qmax(1, 0, n - 1, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return l > r || !n ? POS_INF : qmin(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMax(i, i); }

    // O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
