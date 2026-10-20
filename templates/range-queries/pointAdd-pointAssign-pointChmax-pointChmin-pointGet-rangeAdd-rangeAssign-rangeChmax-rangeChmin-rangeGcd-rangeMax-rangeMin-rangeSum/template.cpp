// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeGcd-rangeMax-rangeMin-rangeSum/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeGcd rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log^2(N)*log(U) amortized ?
//   pointAssign: log^2(N)*log(U) amortized ?
//   pointChmax: log^2(N)*log(U) amortized ?
//   pointChmin: log^2(N)*log(U) amortized ?
//   pointGet: log(N)
//   rangeAdd: log^2(N)*log(U) amortized ?
//   rangeAssign: log^2(N)*log(U) amortized ?
//   rangeChmax: log^2(N)*log(U) amortized ?
//   rangeChmin: log^2(N)*log(U) amortized ?
//   rangeGcd: log(N)*log(U) ?
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N*log(U) ?
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cntMx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N] diffGcd[4*N]
//   tags: addTag[4*N]
//   other: none
//   note: 4n slots per array; every node field and tag is its own flat list
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/rangeChmin-Chmax-Add-Assign-Sum-Min-Max-Gcd-PointSet.cpp

// Segment tree beats with range gcd: range chmin / chmax / add / assign, range sum / min / max / gcd, point ops.
// All indices 0-based, ranges inclusive [l, r]. Each node keeps max / second max / count, min / second min / count,
// the sum, and diffGcd = gcd of pairwise differences among the node's "middle" values (neither its max nor its min).
// Chmin / chmax only move the max / min group, and add shifts everything uniformly, so diffGcd never changes under
// a tag; the node gcd is gcd(diffGcd, mx2 - mx, mn2 - mn, mx). A node with mn == mx pushes down as an assign.
// T: int, long long, ...; sums accumulate in S (long long for small T). Gcds are of absolute values.
template <typename T>
struct BeatsGcd {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    struct Node {
        T mx, mx2, mn, mn2, diffGcd, addTag;
        int cntMx, cntMn;
        S tot;
    };
    int n;
    vector<Node> t;

    static T absT(T x) { return x < 0 ? -x : x; }

    // O(N logU)
    explicit BeatsGcd(const vector<T>& a) : n((int)a.size()), t(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { t[i] = Node{a[tl], NEG_INF, a[tl], POS_INF, 0, 0, 1, 1, S(a[tl])}; return; }
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

    void applyAssign(int i, int sz, T v) { t[i] = Node{v, NEG_INF, v, POS_INF, 0, 0, sz, sz, S(v) * sz}; }

    void applyAdd(int i, int sz, T v) {
        Node& nd = t[i];
        if (nd.mn == nd.mx) { applyAssign(i, sz, nd.mx + v); return; }
        nd.mx += v, nd.mn += v;
        if (nd.mx2 != NEG_INF) nd.mx2 += v;
        if (nd.mn2 != POS_INF) nd.mn2 += v;
        nd.tot += S(v) * sz;
        nd.addTag += v;  // diffGcd untouched: a uniform shift does not change any difference
    }

    void applyChmin(int i, int sz, T v) {
        Node& nd = t[i];
        if (nd.mn >= v) { applyAssign(i, sz, v); return; }
        if (nd.mx > v) {
            if (nd.mn2 == nd.mx) nd.mn2 = v;
            nd.tot -= S(nd.mx - v) * nd.cntMx;
            nd.mx = v;
        }
    }

    void applyChmax(int i, int sz, T v) {
        Node& nd = t[i];
        if (nd.mx <= v) { applyAssign(i, sz, v); return; }
        if (nd.mn < v) {
            if (nd.mx2 == nd.mn) nd.mx2 = v;
            nd.tot += S(v - nd.mn) * nd.cntMn;
            nd.mn = v;
        }
    }

    void push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2, lsz = tm - tl + 1, rsz = tr - tm, l = 2 * i, r = l + 1;
        if (t[i].mn == t[i].mx) { applyAssign(l, lsz, t[i].mx), applyAssign(r, rsz, t[i].mx); return; }
        if (T a = t[i].addTag) applyAdd(l, lsz, a), applyAdd(r, rsz, a), t[i].addTag = 0;
        applyChmin(l, lsz, t[i].mx), applyChmin(r, rsz, t[i].mx);
        applyChmax(l, lsz, t[i].mn), applyChmax(r, rsz, t[i].mn);
    }

    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x >= t[i].mx) return;
        if (ql <= tl && tr <= qr && x > t[i].mx2) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x <= t[i].mn) return;
        if (ql <= tl && tr <= qr && x < t[i].mn2) { applyChmax(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        add(2 * i, tl, tm, ql, qr, v), add(2 * i + 1, tm + 1, tr, ql, qr, v);
        pull(i);
    }

    void assign(int i, int tl, int tr, int ql, int qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, tr - tl + 1, v); return; }
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

    T nodeGcd(int i) const {
        const Node& nd = t[i];
        T g = nd.diffGcd;
        if (nd.mx2 != NEG_INF) g = std::gcd(g, absT(nd.mx2 - nd.mx));
        if (nd.mn2 != POS_INF) g = std::gcd(g, absT(nd.mn2 - nd.mn));
        return std::gcd(g, absT(nd.mx));
    }

    T qgcd(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return nodeGcd(i);
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return std::gcd(qgcd(2 * i, tl, tm, ql, qr), qgcd(2 * i + 1, tm + 1, tr, ql, qr));
    }

    // amortized O(log^2 N logU) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N logU) -- a[i] = max(a[i], x) for i in [l, r]
    void rangeChmax(int l, int r, T x) { if (l <= r && n) chmax(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N logU) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { if (l <= r && n) add(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N logU) -- a[i] = x for i in [l, r]
    void rangeAssign(int l, int r, T x) { if (l <= r && n) assign(1, 0, n - 1, l, r, x); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return l > r || !n ? NEG_INF : qmax(1, 0, n - 1, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return l > r || !n ? POS_INF : qmin(1, 0, n - 1, l, r); }

    // O(logN logU) -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) { return l > r || !n ? T(0) : qgcd(1, 0, n - 1, l, r); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMax(i, i); }

    // a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }

    // a[i] += delta
    void pointAdd(int i, T delta) { rangeAdd(i, i, delta); }
};
