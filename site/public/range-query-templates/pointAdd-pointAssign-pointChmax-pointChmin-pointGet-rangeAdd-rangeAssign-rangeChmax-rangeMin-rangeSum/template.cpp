// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeMin-rangeSum/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeMin rangeSum
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
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N] sz[4*N]
//   tags: addMn[4*N] addOther[4*N] hasAssign[4*N] assignVal[4*N]
//   other: none
//   note: 4n slots per array; every node field and tag is its own flat list
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmax-Add-Assign-Sum-Min-PointSet-Beats.cpp

// Segment tree beats, one side only: range rangeChmax / add / assign, range sum / rangeMin, point ops. 0-based, inclusive.
// Each node keeps its min (mn), strict second min (mn2) and how many times the min appears, plus two add tags: one for
// the min group and one for everything else. A rangeChmax with mn < x < mn2 only moves the min group, so it becomes
// an add on that group alone. Amortized O(log^2 N) with rangeAdd in the mix (O(log N) without).
// T: int, long long, ...; sums accumulate in S (long long for small T). Sentinels are numeric_limits<T>.
template <typename T>
struct BeatsChmax {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T INF = numeric_limits<T>::max();  // "no second min"
    struct Node {
        T mn, mn2, addMn, addOther, assignVal;
        int cntMn, sz;
        S tot;
        bool hasAssign;
    };
    int n;
    vector<Node> t;

    static bool better(T a, T b) { return a < b; }  // a is strictly more extreme than b

    // O(N)
    explicit BeatsChmax(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
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
        Node& nd = t[i];
        if (nd.sz == 1) return;
        int l = 2 * i, r = l + 1;
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

    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || !better(t[i].mn, x)) return;
        if (ql <= tl && tr <= qr && better(x, t[i].mn2)) { applyAdd(i, x - t[i].mn, 0); return; }
        push(i);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
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
        if (ql <= tl && tr <= qr) return t[i].mn;
        push(i);
        int tm = (tl + tr) / 2;
        T a = qext(2 * i, tl, tm, ql, qr), b = qext(2 * i + 1, tm + 1, tr, ql, qr);
        return better(a, b) ? a : b;
    }

    // amortized O(log^2 N) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) { if (l <= r && n) chmax(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { if (l <= r && n) add(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return l > r || !n ? INF : qext(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMin(i, i); }

    // a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v): the other side is not a beats op here, so it is a point assign
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
