// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeChmax-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/template.cpp
// @operations: getAll leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeChmax rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   getAll: N
//   leftmostGtX: log(N)
//   leftmostGteX: log(N)
//   leftmostLtX: log(N)
//   leftmostLteX: log(N)
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   rangeChmax: log(N) amortized
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   rightmostGtX: log(N)
//   rightmostGteX: log(N)
//   rightmostLtX: log(N)
//   rightmostLteX: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mn[4*N] mn2[4*N] cntMn[4*N] tot[4*N]
//   tags: none
//   other: none
//   note: no chmin / chmax / assign tags: a node's own mn is its pending clamp, and a node whose values are all equal pushes that value as an assign

// Segment tree beats: range chmax (a[i] = max(a[i], x)) and range assign, with range sums and the range max / min,
// plus point ops. All indices 0-based, ranges inclusive. How it works: a chmax only changes the min values of a node
// it covers, so a node keeps its min, its strict second min and how many copies of the min it has; a chmax x with mn <
// x < mn2 moves just those copies (the sum rises by (x - mn) * cntMn) and stops there, and only x >= mn2 has to go
// further down. A node's own mn doubles as its pending clamp: push clamps each child to it, so there is no chmin /
// chmax tag. There is no assign tag either: when all of a node's values are equal (no second min), push hands that
// value to both children as an assign. Amortized O(log N) per update (beats: every extra descent removes a distinct
// value).
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ChminChmaxBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    int n;
    vector<T> mx, mn, mn2;
    vector<int> cntMn;
    vector<S> tot;

    // O(N)
    explicit ChminChmaxBeats(const vector<T>& a) : n((int)a.size()), mx(4 * max(1, n)), mn(4 * max(1, n)), mn2(4 * max(1, n), POS_INF), cntMn(4 * max(1, n)), tot(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { mx[i] = a[tl], mn[i] = a[tl], mn2[i] = POS_INF, cntMn[i] = 1, tot[i] = a[tl]; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        int l = 2 * i, r = l + 1;
        tot[i] = tot[l] + tot[r];
        mx[i] = max(mx[l], mx[r]);
        if (mn[l] < mn[r]) mn[i] = mn[l], cntMn[i] = cntMn[l], mn2[i] = min(mn2[l], mn[r]);
        else if (mn[l] > mn[r]) mn[i] = mn[r], cntMn[i] = cntMn[r], mn2[i] = min(mn2[r], mn[l]);
        else mn[i] = mn[l], cntMn[i] = cntMn[l] + cntMn[r], mn2[i] = min(mn2[l], mn2[r]);
    }

    // every value under node i (sz of them) becomes v
    void applyAssign(int i, long long sz, T v) { mx[i] = v, mn[i] = v, mn2[i] = POS_INF, cntMn[i] = sz, tot[i] = S(v) * sz; }

    // chmax by v on node i, with v < mn2: only the copies of the min move
    void applyChmax(int i, long long sz, T v) {
        if (mn[i] < v) {
            tot[i] += S(v - mn[i]) * cntMn[i];
            mn[i] = v;
            if (mx[i] < v) mx[i] = v;
        }
        (void)sz;
    }

    // hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    void push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2, l = 2 * i, r = l + 1;
        long long lsz = tm - tl + 1, rsz = tr - tm;
        if (mn2[i] == POS_INF) { applyAssign(l, lsz, mx[i]), applyAssign(r, rsz, mx[i]); return; }
        applyChmax(l, lsz, mn[i]), applyChmax(r, rsz, mn[i]);
    }

    void chmax(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x <= mn[i]) return;
        if (ql <= tl && tr <= qr && x < mn2[i]) { applyChmax(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmax(2 * i, tl, tm, ql, qr, x), chmax(2 * i + 1, tm + 1, tr, ql, qr, x);
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
        if (ql <= tl && tr <= qr) return tot[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, ql, qr) + qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }

    T qmax(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return mx[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }

    T qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return mn[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(qmin(2 * i, tl, tm, ql, qr), qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }

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

    void getAllRec(int i, int tl, int tr, vector<T>& out) {
        if (tl == tr) { out.push_back(mx[i]); return; }
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

    // amortized O(logN) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // amortized O(logN) -- a[i] += v
    void pointAdd(int i, T v) { rangeAssign(i, i, pointGet(i) + v); }

    // amortized O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { rangeChmax(i, i, v); }

    // amortized O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) rangeAssign(i, i, v); }

    // O(logN) -- the first i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int leftmostGtX(int l, int r, T x) {
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] > x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int leftmostGteX(int l, int r, T x) {
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] >= x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int leftmostLtX(int l, int r, T x) {
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] < x; });
    }

    // O(logN) -- the first i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    int leftmostLteX(int l, int r, T x) {
        return l > r || !n ? -1 : firstPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] <= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] > x, or -1 (a walk pruned by the node max)
    int rightmostGtX(int l, int r, T x) {
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] > x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] >= x, or -1 (a walk pruned by the node max)
    int rightmostGteX(int l, int r, T x) {
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mx[i] >= x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] < x, or -1 (a walk pruned by the node min)
    int rightmostLtX(int l, int r, T x) {
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] < x; });
    }

    // O(logN) -- the last i in [l, r] with a[i] <= x, or -1 (a walk pruned by the node min)
    int rightmostLteX(int l, int r, T x) {
        return l > r || !n ? -1 : lastPass(1, 0, n - 1, l, r, [&](int i) { return mn[i] <= x; });
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
};
