// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAssign-rangeFloorDiv-rangeFloorSqrt-rangeMax-rangeMin-rangeMod-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeFloorDiv rangeFloorSqrt rangeMax rangeMin rangeMod rangeSum
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAssign: log(U) amortized
//   rangeFloorDiv: log(U)*log(U) amortized
//   rangeFloorSqrt: log(U)*log(log(U)) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeMod: log(U)*log(U) amortized
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mn[4*log(U)] tot[4*log(U)]
//   tags: none
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. One shared node pool, call resetPool() between test cases

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root
// is one block of zeros; children are created on demand as blocks of zeros (every count = their length)
// right before anything descends past a node or pushes its tags. Nodes live in one pool shared by every
// SparseShrinkSeg<T> (resetPool() between test cases). Otherwise the beats logic below is the dense tree's, with
// children in Lc / Rc instead of at 2i / 2i + 1.

// "Shrink" segment tree with range assign: range mod / floor-div / floor-sqrt / assign, range sum / min / max,
// point ops. All indices 0-based, ranges inclusive. Values must be >= 0.
// No tag arrays: a uniform node (mn == mx) IS the assign tag, and is pushed to children as such. A shrink op on a
// fully covered uniform node is applied in O(1); otherwise it descends, pruning subtrees whose max is below the
// cutoff. Assign collapses a node to one value, so it can only drain the "distinct values" potential.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct SparseShrinkSeg {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static inline vector<T> mx = vector<T>(1);
    static inline vector<T> mn = vector<T>(1);
    static inline vector<S> tot = vector<S>(1);
    static inline vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    static inline vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseShrinkSeg(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }

    // O(1) -- forget every node of every SparseShrinkSeg<T>; call between test cases, then build new trees
    static void resetPool() { mx.resize(1); mn.resize(1); tot.resize(1); Lc.resize(1); Rc.resize(1); ln.resize(1); }

    // optional -- reserve room for this many nodes up front
    static void reservePool(size_t nodes) { mx.reserve(nodes); mn.reserve(nodes); tot.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only touches the shared pool
        mx.push_back(0); mn.push_back(0); tot.push_back(0);
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }

    void pull(int i) {
        mx[i] = max(mx[Lc[i]], mx[Rc[i]]), mn[i] = min(mn[Lc[i]], mn[Rc[i]]);
        tot[i] = tot[Lc[i]] + tot[Rc[i]];
    }

    void applyAssign(int i, long long sz, T v) { mx[i] = mn[i] = v, tot[i] = S(v) * sz; }

    // mn == mx is the assign tag: every value below a uniform node is that number
    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr || mn[i] != mx[i]) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        applyAssign(Lc[i], tm - tl + 1, mx[i]), applyAssign(Rc[i], tr - tm, mx[i]);
    }

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrink(int i, long long tl, long long tr, long long ql, long long qr, T cutoff, const F& op) {
        if (qr < tl || ql > tr || mx[i] < cutoff) return;
        if (ql <= tl && tr <= qr && mn[i] == mx[i]) { applyAssign(i, tr - tl + 1, op(mx[i])); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        shrink(Lc[i], tl, tm, ql, qr, cutoff, op), shrink(Rc[i], tm + 1, tr, ql, qr, cutoff, op);
        pull(i);
    }

    void assign(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAssign(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        assign(Lc[i], tl, tm, ql, qr, v), assign(Rc[i], tm + 1, tr, ql, qr, v);
        pull(i);
    }

    S qsum(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return 0;
        if (ql <= tl && tr <= qr) return tot[i];
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return qsum(Lc[i], tl, tm, ql, qr) + qsum(Rc[i], tm + 1, tr, ql, qr);
    }

    T qmax(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return numeric_limits<T>::lowest();
        if (ql <= tl && tr <= qr) return mx[i];
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(Lc[i], tl, tm, ql, qr), qmax(Rc[i], tm + 1, tr, ql, qr));
    }

    T qmin(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return numeric_limits<T>::max();
        if (ql <= tl && tr <= qr) return mn[i];
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return min(qmin(Lc[i], tl, tm, ql, qr), qmin(Rc[i], tm + 1, tr, ql, qr));
    }

    // amortized O(logN logU) -- a[i] %= x for i in [l, r]; prunes at max < x, where a % x == a
    void rangeMod(long long l, long long r, T x) {
        if (l <= r && x >= 1) shrink(root, lo, hi, l, r, x, [x](T v) { return v % x; });
    }

    // amortized O(logN logU) -- a[i] /= x (floor) for i in [l, r]; requires x >= 2, prunes at max < 1
    void rangeFloorDiv(long long l, long long r, T x) {
        if (l <= r && x >= 2) shrink(root, lo, hi, l, r, T(1), [x](T v) { return v / x; });
    }

    // amortized O(logN loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r]; 0 and 1 are fixed points
    void rangeFloorSqrt(long long l, long long r) {
        if (l <= r) shrink(root, lo, hi, l, r, T(2), isqrtT);
    }

    // amortized O(logN) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) { if (l <= r) assign(root, lo, hi, l, r, v); }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logN) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return qmax(root, lo, hi, l, r); }

    // O(logN) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return qmin(root, lo, hi, l, r); }

    // O(logN) -- a[i] = v, an overwrite that may raise the value
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // O(logN) -- a[i]
    T pointGet(long long i) { return rangeMax(i, i); }

    // a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // a[i] += delta (the result must stay >= 0)
    void pointAdd(long long i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
