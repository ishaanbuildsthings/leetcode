// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmin-rangeMax-rangeMin-rangeSum/template.cpp
// @operations: getAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeMin rangeSum
// @data-structure-type: beats
// @complexities:
//   getAll: N
//   pointAdd: log^2(N) amortized
//   pointAssign: log^2(N) amortized
//   pointChmax: log^2(N) amortized
//   pointChmin: log^2(N) amortized
//   pointGet: log(N)
//   rangeAdd: log^2(N) amortized
//   rangeAssign: log^2(N) amortized
//   rangeChmin: log^2(N) amortized
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mx2[4*N] cntMx[4*N] mn[4*N] tot[4*N]
//   tags: addTag[4*N]
//   other: none
//   note: no chmin / chmax / assign tags: a node's own mx is its pending clamp, and a node whose values are all equal pushes that value as an assign

// Segment tree beats: range chmin (a[i] = min(a[i], x)), range add and range assign, with range sums and the range max
// / min, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only changes the max values of a
// node it covers, so a node keeps its max, its strict second max and how many copies of the max it has; a chmin x with
// mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops there, and only x <= mx2 has to
// go further down. A node's own mx doubles as its pending clamp: push clamps each child to it, so there is no chmin /
// chmax tag. There is no assign tag either: when all of a node's values are equal (no second max), push hands that
// value to both children as an assign. An add shifts everything a node keeps and goes in the one add tag. Amortized
// O(log^2 N) per update with range add, O(log N) without it (beats: every extra descent removes a distinct value).
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct ChminChmaxBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    int n;
    vector<T> mx, mx2, mn, addTag;
    vector<int> cntMx;
    vector<S> tot;

    // O(N)
    explicit ChminChmaxBeats(const vector<T>& a) : n((int)a.size()), mx(4 * max(1, n)), mx2(4 * max(1, n), NEG_INF), mn(4 * max(1, n)), addTag(4 * max(1, n)), cntMx(4 * max(1, n)), tot(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { mx[i] = a[tl], mx2[i] = NEG_INF, cntMx[i] = 1, mn[i] = a[tl], tot[i] = a[tl]; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        int l = 2 * i, r = l + 1;
        tot[i] = tot[l] + tot[r];
        if (mx[l] > mx[r]) mx[i] = mx[l], cntMx[i] = cntMx[l], mx2[i] = max(mx2[l], mx[r]);
        else if (mx[l] < mx[r]) mx[i] = mx[r], cntMx[i] = cntMx[r], mx2[i] = max(mx2[r], mx[l]);
        else mx[i] = mx[l], cntMx[i] = cntMx[l] + cntMx[r], mx2[i] = max(mx2[l], mx2[r]);
        mn[i] = min(mn[l], mn[r]);
        addTag[i] = 0;
    }

    // every value under node i (sz of them) becomes v
    void applyAssign(int i, long long sz, T v) { mx[i] = v, mx2[i] = NEG_INF, cntMx[i] = sz, mn[i] = v, tot[i] = S(v) * sz, addTag[i] = 0; }

    // every value under node i gains v
    void applyAdd(int i, long long sz, T v) {
        if (mx2[i] == NEG_INF) { applyAssign(i, sz, mx[i] + v); return; }
        mx[i] += v;
        if (mx2[i] != NEG_INF) mx2[i] += v;
        mn[i] += v;
        tot[i] += S(v) * sz, addTag[i] += v;
    }

    // chmin by v on node i, with mx2 < v: only the copies of the max move
    void applyChmin(int i, long long sz, T v) {
        if (mx[i] > v) {
            tot[i] -= S(mx[i] - v) * cntMx[i];
            mx[i] = v;
            if (mn[i] > v) mn[i] = v;
        }
        (void)sz;
    }

    // hand node i's pending changes to its children: all one value (an assign), else the add, then its own clamp
    void push(int i, int tl, int tr) {
        if (tl == tr) return;
        int tm = (tl + tr) / 2, l = 2 * i, r = l + 1;
        long long lsz = tm - tl + 1, rsz = tr - tm;
        if (mx2[i] == NEG_INF) { applyAssign(l, lsz, mx[i]), applyAssign(r, rsz, mx[i]); return; }
        if (T a = addTag[i]) applyAdd(l, lsz, a), applyAdd(r, rsz, a), addTag[i] = 0;
        applyChmin(l, lsz, mx[i]), applyChmin(r, rsz, mx[i]);
    }

    void chmin(int i, int tl, int tr, int ql, int qr, T x) {
        if (qr < tl || ql > tr || x >= mx[i]) return;
        if (ql <= tl && tr <= qr && x > mx2[i]) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        chmin(2 * i, tl, tm, ql, qr, x), chmin(2 * i + 1, tm + 1, tr, ql, qr, x);
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

    // amortized O(log^2 N) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(int l, int r, T x) { if (l <= r && n) chmin(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N) -- a[i] += x for i in [l, r]
    void rangeAdd(int l, int r, T x) { if (l <= r && n) add(1, 0, n - 1, l, r, x); }

    // amortized O(log^2 N) -- a[i] = x for i in [l, r]
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

    // amortized O(log^2 N) -- a[i] = v
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // amortized O(log^2 N) -- a[i] += v
    void pointAdd(int i, T v) { rangeAdd(i, i, v); }

    // amortized O(log^2 N) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) rangeAssign(i, i, v); }

    // amortized O(log^2 N) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { rangeChmin(i, i, v); }
};
