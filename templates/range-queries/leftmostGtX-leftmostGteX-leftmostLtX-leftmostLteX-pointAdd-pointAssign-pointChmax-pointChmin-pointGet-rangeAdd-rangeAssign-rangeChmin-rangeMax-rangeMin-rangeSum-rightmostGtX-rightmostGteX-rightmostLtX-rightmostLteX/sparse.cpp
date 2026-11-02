// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAssign-rangeChmin-rangeMax-rangeMin-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse.cpp
// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAssign rangeChmin rangeMax rangeMin rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)*log(U) amortized
//   pointAssign: log(U)*log(U) amortized
//   pointChmax: log(U)*log(U) amortized
//   pointChmin: log(U)*log(U) amortized
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) amortized
//   rangeAssign: log(U)*log(U) amortized
//   rangeChmin: log(U)*log(U) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mx2[4*log(U)] cntMx[4*log(U)] mn[4*log(U)] tot[4*log(U)]
//   tags: addTag[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Segment tree beats: range chmin (a[i] = min(a[i], x)), range add and range assign, with range sums and the range max
// / min, plus point ops. All indices 0-based, ranges inclusive. How it works: a chmin only changes the max values of a
// node it covers, so a node keeps its max, its strict second max and how many copies of the max it has; a chmin x with
// mx2 < x < mx moves just those copies (the sum drops by (mx - x) * cntMx) and stops there, and only x <= mx2 has to
// go further down. A node's own mx doubles as its pending clamp: push clamps each child to it, so there is no chmin /
// chmax tag. There is no assign tag either: when all of a node's values are equal (no second max), push hands that
// value to both children as an assign. An add shifts everything a node keeps and goes in the one add tag. Amortized
// O(log^2 U) per update with range add, O(log U) without it (beats: every extra descent removes a distinct value).
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseChminChmaxBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    static constexpr T NEG_INF = numeric_limits<T>::lowest(), POS_INF = numeric_limits<T>::max();
    mutable vector<T> mx = vector<T>(1);
    mutable vector<T> mx2 = vector<T>(1);
    mutable vector<T> mn = vector<T>(1);
    mutable vector<T> addTag = vector<T>(1);
    mutable vector<long long> cntMx = vector<long long>(1);
    mutable vector<S> tot = vector<S>(1);
    mutable vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseChminChmaxBeats(long long lo, long long hi) : lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { mx.reserve(nodes); mx2.reserve(nodes); mn.reserve(nodes); addTag.reserve(nodes); cntMx.reserve(nodes); tot.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        mx.push_back(0); mx2.push_back(NEG_INF); mn.push_back(0); addTag.push_back(0); cntMx.push_back(k); tot.push_back(0);
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
        int l = Lc[i], r = Rc[i];
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
    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2, l = Lc[i], r = Rc[i];
        long long lsz = tm - tl + 1, rsz = tr - tm;
        if (mx2[i] == NEG_INF) { applyAssign(l, lsz, mx[i]), applyAssign(r, rsz, mx[i]); return; }
        if (T a = addTag[i]) applyAdd(l, lsz, a), applyAdd(r, rsz, a), addTag[i] = 0;
        applyChmin(l, lsz, mx[i]), applyChmin(r, rsz, mx[i]);
    }

    void chmin(int i, long long tl, long long tr, long long ql, long long qr, T x) {
        if (qr < tl || ql > tr || x >= mx[i]) return;
        if (ql <= tl && tr <= qr && x > mx2[i]) { applyChmin(i, tr - tl + 1, x); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        chmin(Lc[i], tl, tm, ql, qr, x), chmin(Rc[i], tm + 1, tr, ql, qr, x);
        pull(i);
    }

    void add(int i, long long tl, long long tr, long long ql, long long qr, T v) {
        if (qr < tl || ql > tr) return;
        if (ql <= tl && tr <= qr) { applyAdd(i, tr - tl + 1, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        add(Lc[i], tl, tm, ql, qr, v), add(Rc[i], tm + 1, tr, ql, qr, v);
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
        if (qr < tl || ql > tr) return NEG_INF;
        if (ql <= tl && tr <= qr) return mx[i];
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return max(qmax(Lc[i], tl, tm, ql, qr), qmax(Rc[i], tm + 1, tr, ql, qr));
    }

    T qmin(int i, long long tl, long long tr, long long ql, long long qr) {
        if (qr < tl || ql > tr) return POS_INF;
        if (ql <= tl && tr <= qr) return mn[i];
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        return min(qmin(Lc[i], tl, tm, ql, qr), qmin(Rc[i], tm + 1, tr, ql, qr));
    }

    // amortized O(log^2 U) -- a[i] = min(a[i], x) for i in [l, r]
    void rangeChmin(long long l, long long r, T x) { if (l <= r) chmin(root, lo, hi, l, r, x); }

    // amortized O(log^2 U) -- a[i] += x for i in [l, r]
    void rangeAdd(long long l, long long r, T x) { if (l <= r) add(root, lo, hi, l, r, x); }

    // amortized O(log^2 U) -- a[i] = x for i in [l, r]
    void rangeAssign(long long l, long long r, T x) { if (l <= r) assign(root, lo, hi, l, r, x); }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) { return l > r ? S(0) : qsum(root, lo, hi, l, r); }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) { return l > r ? NEG_INF : qmax(root, lo, hi, l, r); }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) { return l > r ? POS_INF : qmin(root, lo, hi, l, r); }

    // O(logU) -- a[i]
    T pointGet(long long i) { return rangeMax(i, i); }

    // amortized O(log^2 U) -- a[i] = v
    void pointAssign(long long i, T v) { rangeAssign(i, i, v); }

    // amortized O(log^2 U) -- a[i] += v
    void pointAdd(long long i, T v) { rangeAdd(i, i, v); }

    // amortized O(log^2 U) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) { if (v > pointGet(i)) rangeAssign(i, i, v); }

    // amortized O(log^2 U) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) { rangeChmin(i, i, v); }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    long long leftmostGtX(long long l, long long r, T x) {
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mx[i] > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    long long leftmostGteX(long long l, long long r, T x) {
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mx[i] >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLtX(long long l, long long r, T x) {
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mn[i] < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLteX(long long l, long long r, T x) {
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mn[i] <= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    long long rightmostGtX(long long l, long long r, T x) {
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mx[i] > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    long long rightmostGteX(long long l, long long r, T x) {
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mx[i] >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLtX(long long l, long long r, T x) {
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mn[i] < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLteX(long long l, long long r, T x) {
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mn[i] <= x; });
        return res == NONE ? lo - 1 : res;
    }

    static constexpr long long NONE = LLONG_MIN;  // ("no index": any long long can be an index here)

    // the first index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long firstPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = firstPass(Lc[i], tl, tm, l, r, ok);
        return res != NONE ? res : firstPass(Rc[i], tm + 1, tr, l, r, ok);
    }

    // the last index in [l, r] under node i whose value passes ok(node), or NONE: O(logU), since only one
    // node fully inside [l, r] that passes is ever walked down (it always holds an answer)
    template <class F>
    long long lastPass(int i, long long tl, long long tr, long long l, long long r, const F& ok) {
        if (r < tl || tr < l || !ok(i)) return NONE;
        if (tl == tr) return tl;
        push(i, tl, tr), kids(i);
        long long tm = tl + (tr - tl) / 2, res = lastPass(Rc[i], tm + 1, tr, l, r, ok);
        return res != NONE ? res : lastPass(Lc[i], tl, tm, l, r, ok);
    }
};