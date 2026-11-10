// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmax-rangeChmin-rangeGcd-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/template.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: gcdAll getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX maxAll minAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmax rangeChmin rangeGcd rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX sumAll
// @data-structure-type: beats
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
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
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   sumAll: log(N)
//   minAll: log(N)
//   maxAll: log(N)
//   gcdAll: log(N)*log(U) ?
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

    // amortized O(log^2 N logU) -- a[i] = min(a[i], x) for i in [l, r]; needs 0 <= l <= r < n, else throws
    // out_of_range
    void rangeChmin(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeChmin: needs 0 <= l <= r < n");
        if (l <= r && n) chmin(1, 0, n - 1, l, r, x);
    }

    // amortized O(log^2 N logU) -- a[i] = max(a[i], x) for i in [l, r]; needs 0 <= l <= r < n, else throws
    // out_of_range
    void rangeChmax(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeChmax: needs 0 <= l <= r < n");
        if (l <= r && n) chmax(1, 0, n - 1, l, r, x);
    }

    // amortized O(log^2 N logU) -- a[i] += x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAdd(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAdd: needs 0 <= l <= r < n");
        if (l <= r && n) add(1, 0, n - 1, l, r, x);
    }

    // amortized O(log^2 N logU) -- a[i] = x for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAssign(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAssign: needs 0 <= l <= r < n");
        if (l <= r && n) assign(1, 0, n - 1, l, r, x);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r);
    }

    // O(logN) -- max of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMax(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMax: needs 0 <= l <= r < n");
        return l > r || !n ? NEG_INF : qmax(1, 0, n - 1, l, r);
    }

    // O(logN) -- min of a[l..r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeMin(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeMin: needs 0 <= l <= r < n");
        return l > r || !n ? POS_INF : qmin(1, 0, n - 1, l, r);
    }

    // O(logN logU) -- gcd of |a[l]|, ..., |a[r]|; needs 0 <= l <= r < n, else throws out_of_range
    T rangeGcd(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeGcd: needs 0 <= l <= r < n");
        return l > r || !n ? T(0) : qgcd(1, 0, n - 1, l, r);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return rangeMax(i, i);
    }

    void getAllRec(int i, int tl, int tr, vector<T>& out) {
        if (tl == tr) { out.push_back(t[i].mx); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        getAllRec(2 * i, tl, tm, out), getAllRec(2 * i + 1, tm + 1, tr, out);
    }

    // O(N) -- the whole array: one DFS that pushes every tag down and reads the leaves left to right
    vector<T> getAll() {
        vector<T> out;
        out.reserve(n);
        if (n) getAllRec(1, 0, n - 1, out);
        return out;
    }

    // O(log^2 N * logU) amortized -- a[i] = v; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        rangeAssign(i, i, v);
    }

    // O(log^2 N * logU) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        rangeChmax(i, i, v);
    }

    // O(log^2 N * logU) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        rangeChmin(i, i, v);
    }

    // O(log^2 N * logU) amortized -- a[i] += delta; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        rangeAdd(i, i, delta);
    }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mx > x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostGteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mx >= x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mn < x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int leftmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("leftmostLteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mn <= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostGtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mx > x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostGteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostGteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mx >= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostLtX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLtX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mn < x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min); needs 0 <= l <= r < n,
    // else throws out_of_range
    int rightmostLteX(int l, int r, T x) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rightmostLteX: needs 0 <= l <= r < n");
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return t[i].mn <= x; });
    }

    // the first index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    int firstPass(int i, int tl, int tr, int l, int r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return -1;
        if (tl == tr) return tl;
        push(i, tl, tr);
        int tm = (tl + tr) / 2, res = firstPass(2 * i, tl, tm, l, r, ok);
        return res != -1 ? res : firstPass(2 * i + 1, tm + 1, tr, l, r, ok);
    }

    // the last index in [l, r] under node i whose value passes ok(node), or -1: O(logN), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    int lastPass(int i, int tl, int tr, int l, int r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return -1;
        if (tl == tr) return tl;
        push(i, tl, tr);
        int tm = (tl + tr) / 2, res = lastPass(2 * i + 1, tm + 1, tr, l, r, ok);
        return res != -1 ? res : lastPass(2 * i, tl, tm, l, r, ok);
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- min of the whole array a[0..n-1] (rangeMin(0, n - 1)); needs n >= 1, else throws out_of_range
    auto minAll() {
        if (n < 1) throw out_of_range("minAll: needs n >= 1");
        return rangeMin(0, n - 1);
    }

    // O(log(N)) -- max of the whole array a[0..n-1] (rangeMax(0, n - 1)); needs n >= 1, else throws out_of_range
    auto maxAll() {
        if (n < 1) throw out_of_range("maxAll: needs n >= 1");
        return rangeMax(0, n - 1);
    }

    // O(log(N)*log(U) ?) -- gcd of the whole array a[0..n-1] (rangeGcd(0, n - 1)); needs n >= 1, else throws
    // out_of_range
    auto gcdAll() {
        if (n < 1) throw out_of_range("gcdAll: needs n >= 1");
        return rangeGcd(0, n - 1);
    }

};
