// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeFloorDiv rangeFloorSqrt rangeMax rangeMod rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(N)
//   pointAssign: log(N)
//   pointChmax: log(N)
//   pointChmin: log(N)
//   pointGet: log(N)
//   rangeFloorDiv: log(N)*log(U) amortized
//   rangeFloorSqrt: log(N)*log(log(U)) amortized
//   rangeMax: log(N)
//   rangeMod: log(N)*log(U) amortized
//   rangeSum: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mx[4*N] tot[4*N]
//   tags: none
//   other: none
//   note: no lazy tags: updates walk down to the leaves that still shrink
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-Mod-Sum-FloorDiv-Sqrt-pointAssign.cpp

// "Shrink" segment tree: range mod / floor-div / floor-sqrt, range sum / max, point ops. 0-based, inclusive.
// No lazy tags: an update walks down to every leaf that will actually change, pruning any subtree whose max is
// below the op's cutoff. Each such leaf at least halves (mod, div) or square-roots, so each value can only be hit
// O(log U) (or O(log log U)) times between point assigns. Values must be >= 0.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct ShrinkTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    vector<T> mx;
    vector<S> tot;

    // O(N)
    explicit ShrinkTree(const vector<T>& a) : n((int)a.size()), mx(4 * max(1, n)), tot(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void pull(int i) { mx[i] = max(mx[2 * i], mx[2 * i + 1]), tot[i] = tot[2 * i] + tot[2 * i + 1]; }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { mx[i] = a[tl], tot[i] = a[tl]; return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    // descend to the leaves that change; cutoff = smallest value the op can change
    template <class F>
    void shrink(int i, int tl, int tr, int ql, int qr, T cutoff, const F& op) {
        if (qr < tl || ql > tr || mx[i] < cutoff) return;
        if (tl == tr) { mx[i] = op(mx[i]), tot[i] = mx[i]; return; }
        int tm = (tl + tr) / 2;
        shrink(2 * i, tl, tm, ql, qr, cutoff, op), shrink(2 * i + 1, tm + 1, tr, ql, qr, cutoff, op);
        pull(i);
    }

    void set(int i, int tl, int tr, int p, T v) {
        if (tl == tr) { mx[i] = v, tot[i] = v; return; }
        int tm = (tl + tr) / 2;
        if (p <= tm) set(2 * i, tl, tm, p, v);
        else set(2 * i + 1, tm + 1, tr, p, v);
        pull(i);
    }

    S qsum(int i, int tl, int tr, int ql, int qr) const {
        if (ql > tr || qr < tl) return 0;
        if (ql <= tl && tr <= qr) return tot[i];
        int tm = (tl + tr) / 2;
        return qsum(2 * i, tl, tm, ql, qr) + qsum(2 * i + 1, tm + 1, tr, ql, qr);
    }

    T qmax(int i, int tl, int tr, int ql, int qr) const {
        if (ql > tr || qr < tl) return numeric_limits<T>::lowest();
        if (ql <= tl && tr <= qr) return mx[i];
        int tm = (tl + tr) / 2;
        return max(qmax(2 * i, tl, tm, ql, qr), qmax(2 * i + 1, tm + 1, tr, ql, qr));
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

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) const { return l > r || !n ? S(0) : qsum(1, 0, n - 1, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(int l, int r) const { return l > r || !n ? numeric_limits<T>::lowest() : qmax(1, 0, n - 1, l, r); }

    // O(logN) -- a[i] = v, an overwrite that may raise the value
    void pointAssign(int i, T v) { set(1, 0, n - 1, i, v); }

    // O(logN) -- a[i]
    T pointGet(int i) const { return rangeMax(i, i); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] += delta (the result must stay >= 0)
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
