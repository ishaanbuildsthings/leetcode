// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMin-rangeMod-rangeSum/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeFloorDiv rangeFloorSqrt rangeMax rangeMin rangeMod rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAssign: log(N) amortized
//   rangeFloorDiv: log(N)*log(U) amortized
//   rangeFloorSqrt: log(N)*log(log(U)) amortized
//   rangeMax: log(N)
//   rangeMin: log(N)
//   rangeMod: log(N)*log(U) amortized
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] mn[4*N] tot[4*N]
//   tags: none
//   other: none
//   note: no tag arrays: an assigned range is a uniform node (max == min) and is pushed to children as such
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-Mod-Sum-FloorDiv-Sqrt-Min-Max-Assign.cpp

// "Shrink" segment tree with range assign: range mod / floor-div / floor-sqrt / assign, range sum / min / max,
// point ops. All indices 0-based, ranges inclusive. Values must be >= 0.
// No tag arrays: a uniform node (mn == mx) IS the assign tag, and is pushed to children as such. A shrink op on a
// fully covered uniform node is applied in O(1); otherwise it descends, pruning subtrees whose max is below the
// cutoff. Assign collapses a node to one value, so it can only drain the "distinct values" potential.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct ShrinkSeg {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<T> mx, mn;
    vector<S> tot;

    // O(N)
    explicit ShrinkSeg(const vector<T>& a) : n((int)a.size()), mx(4 * max(1, n)), mn(4 * max(1, n)), tot(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void pull(int i) {
        mx[i] = max(mx[2 * i], mx[2 * i + 1]), mn[i] = min(mn[2 * i], mn[2 * i + 1]);
        tot[i] = tot[2 * i] + tot[2 * i + 1];
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { mx[i] = mn[i] = a[tl], tot[i] = a[tl]; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void applyAssign(int i, int sz, T v) { mx[i] = mn[i] = v, tot[i] = S(v) * sz; }

    // mn == mx is the assign tag: every value below a uniform node is that number
    void push(int i, int tl, int tr) {
        if (tl == tr || mn[i] != mx[i]) return;
        int tm = (tl + tr) / 2;
        applyAssign(2 * i, tm - tl + 1, mx[i]), applyAssign(2 * i + 1, tr - tm, mx[i]);
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrink(int i, int tl, int tr, int ql, int qr, T cutoff, const F& op) {
        if (qr < tl || ql > tr || mx[i] < cutoff) return;
        if (ql <= tl && tr <= qr && mn[i] == mx[i]) { applyAssign(i, tr - tl + 1, op(mx[i])); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        shrink(2 * i, tl, tm, ql, qr, cutoff, op), shrink(2 * i + 1, tm + 1, tr, ql, qr, cutoff, op);
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
        if (qr < tl || ql > tr) return numeric_limits<T>::lowest();
        if (ql <= tl && tr <= qr) return mx[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
    }

    T qmin(int i, int tl, int tr, int ql, int qr) {
        if (qr < tl || ql > tr) return numeric_limits<T>::max();
        if (ql <= tl && tr <= qr) return mn[i];
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        return min(qmin(2 * i, tl, tm, ql, qr), qmin(2 * i + 1, tm + 1, tr, ql, qr));
    }

    // amortized O(logN logU) -- a[i] %= x for i in [l, r]; prunes at max < x, where a % x == a
    void rangeMod(int l, int r, T x) {
        if (l <= r && n && x >= 1) shrink(1, 0, n - 1, l, r, x, [x](T v) { return v % x; });
    }

    // amortized O(logN logU) -- a[i] /= x (floor) for i in [l, r]; requires x >= 2, prunes at max < 1
    void rangeFloorDiv(int l, int r, T x) {
        if (l <= r && n && x >= 2) shrink(1, 0, n - 1, l, r, T(1), [x](T v) { return v / x; });
    }

    // amortized O(logN loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r]; 0 and 1 are fixed points
    void rangeFloorSqrt(int l, int r) {
        if (l <= r && n) shrink(1, 0, n - 1, l, r, T(2), isqrtT);
    }

    // amortized O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(int l, int r, T v) { if (l <= r && n) assign(1, 0, n - 1, l, r, v); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) { return qmax(1, 0, n - 1, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return qmin(1, 0, n - 1, l, r); }

    // O(logN) -- a[i] = v, an overwrite that may raise the value
    void pointAssign(int i, T v) { rangeAssign(i, i, v); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeMax(i, i); }

    // a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // a[i] += delta (the result must stay >= 0)
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
