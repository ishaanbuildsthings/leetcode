// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/leftmostGtX-leftmostGteX-leftmostLtX-leftmostLteX-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMax-rangeMin-rangeOrApply-rangeOrQuery-rangeSum-rightmostGtX-rightmostGteX-rightmostLtX-rightmostLteX/sparse.cpp
// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMax rangeMin rangeOrApply rangeOrQuery rangeSum rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U) amortized
//   pointAssign: log(U) amortized
//   pointChmax: log(U) amortized
//   pointChmin: log(U) amortized
//   pointGet: log(U)
//   rangeAndApply: log(U)*log(U) amortized
//   rangeAndQuery: log(U)
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeOrApply: log(U)*log(U) amortized
//   rangeOrQuery: log(U)
//   rangeSum: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: mx[4*log(U)] mn[4*log(U)] tot[4*log(U)] andAll[4*log(U)] orAll[4*log(U)]
//   tags: tagAnd[4*log(U)] tagXor[4*log(U)]
//   other: none
//   note: per update, the nodes it visits (and their siblings, created as blocks of zeros); beats recursion is amortized, so count nodes by work done. A node pool per tree

// Sparse version: any index range [lo, hi] (huge or negative is fine), every position starting at 0. The root is one
// block of zeros; children are created on demand as blocks of zeros (every count = their length) right before anything
// descends past a node or pushes its tags. Nodes live in a pool the tree owns. Otherwise the beats logic below is the
// dense tree's, with children in Lc / Rc instead of at 2i / 2i + 1.

// Bitwise segment tree beats: range and= / or=, range max / min / sum / and / or, point ops.
// All indices 0-based, ranges inclusive. Values live in [0, 2^bits). Every update is the map v -> (v & a) ^ x:
//   and X -> (X, 0)   or X -> (~X, X)
// and those compose into one (and, xor) tag. A tag may only be applied to a whole node when every bit the node's
// values DISAGREE on is merely kept (mixed & (~a | x) == 0): then every value moves by the same delta, so max / min / sum just shift.
// Otherwise recurse; each recursion makes a mixed bit uniform, which pays for it.
// No range xor: xor flips a mixed bit without making it uniform, so it could recurse to every leaf, O(N) per op.
// For xor with sums use BitCountTree (per-bit counts), which needs no beats at all.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct SparseBitBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    T FULL;
    mutable vector<T> mx = vector<T>(1);
    mutable vector<T> mn = vector<T>(1);
    mutable vector<T> andAll = vector<T>(1);
    mutable vector<T> orAll = vector<T>(1);
    mutable vector<T> tagAnd = vector<T>(1);
    mutable vector<T> tagXor = vector<T>(1);
    mutable vector<S> tot = vector<S>(1);
    mutable vector<int> Lc{0}, Rc{0};  // children (0: none yet)
    mutable vector<long long> ln{0};   // how many positions each node covers
    long long lo, hi;
    int root;

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseBitBeats(long long lo, long long hi, int bits = 20) : FULL(T((T(1) << bits) - 1)), lo(lo), hi(hi) { root = node(hi - lo + 1); }


    // optional -- reserve room for this many nodes up front
    void reservePool(size_t nodes) { mx.reserve(nodes); mn.reserve(nodes); andAll.reserve(nodes); orAll.reserve(nodes); tagAnd.reserve(nodes); tagXor.reserve(nodes); tot.reserve(nodes); Lc.reserve(nodes); Rc.reserve(nodes); ln.reserve(nodes); }

    // a fresh node: a block of k zeros
    int node(long long k) const {  // const: it only grows the (mutable) pool
        mx.push_back(0); mn.push_back(0); andAll.push_back(0); orAll.push_back(0); tagAnd.push_back(FULL); tagXor.push_back(0); tot.push_back(0);
        Lc.push_back(0), Rc.push_back(0), ln.push_back(k);
        return (int)ln.size() - 1;
    }

    // create node i's children (blocks of zeros: the left one gets the extra position) if it has none yet
    void kids(int i) const {
        if (Lc[i] || ln[i] <= 1) return;
        int a = node((ln[i] + 1) / 2), b = node(ln[i] / 2);
        Lc[i] = a, Rc[i] = b;
    }

    void setLeaf(int i, T v) {
        mx[i] = mn[i] = andAll[i] = orAll[i] = v, tot[i] = v;
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    void pull(int i) {
        int l = Lc[i], r = Rc[i];
        mx[i] = max(mx[l], mx[r]);
        mn[i] = min(mn[l], mn[r]);
        tot[i] = tot[l] + tot[r];
        andAll[i] = andAll[l] & andAll[r], orAll[i] = orAll[l] | orAll[r];
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // only legal when the node's mixed bits are all kept, so every value shifts by the same delta (k = the node's length)
    void apply(int i, T a, T x, long long k) {
        T keep = (a ^ x) & FULL;
        T delta = (~orAll[i] & x & FULL) - (andAll[i] & ~keep & FULL);
        mx[i] += delta, mn[i] += delta, tot[i] += S(delta) * k;
        andAll[i] = ((andAll[i] & a) ^ x) & FULL, orAll[i] = ((orAll[i] & a) ^ x) & FULL;
        tagAnd[i] = tagAnd[i] & a & FULL, tagXor[i] = ((tagXor[i] & a) ^ x) & FULL;
    }

    void push(int i, long long tl, long long tr) {
        kids(i);
        if (tl == tr || (tagAnd[i] == FULL && tagXor[i] == 0)) return;
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        apply(Lc[i], tagAnd[i], tagXor[i], tm - tl + 1), apply(Rc[i], tagAnd[i], tagXor[i], tr - tm);
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // (v & a) ^ x == v for every v in the node? keep bits are fine, flip bits never are, force-0 needs all 0,
    // force-1 needs all 1
    bool noEffect(int i, T a, T x) const {
        if (a & x & FULL) return false;
        if (~a & ~x & orAll[i] & FULL) return false;
        if (~a & x & ~andAll[i] & FULL) return false;
        return true;
    }

    void upd(int i, long long tl, long long tr, long long ql, long long qr, T a, T x) {
        if (qr < tl || ql > tr || noEffect(i, a, x)) return;
        T mixed = (andAll[i] ^ orAll[i]) & FULL;
        if (ql <= tl && tr <= qr && (mixed & (~a | x) & FULL) == 0) { apply(i, a, x, tr - tl + 1); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        upd(Lc[i], tl, tm, ql, qr, a, x), upd(Rc[i], tm + 1, tr, ql, qr, a, x);
        pull(i);
    }

    void set(int i, long long tl, long long tr, long long p, T v) {
        if (tl == tr) { setLeaf(i, v); return; }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        if (p <= tm) set(Lc[i], tl, tm, p, v);
        else set(Rc[i], tm + 1, tr, p, v);
        pull(i);
    }

    // kind: 0 max, 1 min, 2 sum, 3 and, 4 or; identities are valid because every value is in [0, FULL]
    S query(int i, long long tl, long long tr, long long ql, long long qr, int kind) {
        if (qr < tl || ql > tr) {
            switch (kind) {
                case 0: return S(0);
                case 1: return S(FULL);
                case 2: return S(0);
                case 3: return S(FULL);
                default: return S(0);
            }
        }
        if (ql <= tl && tr <= qr) {
            switch (kind) {
                case 0: return mx[i];
                case 1: return mn[i];
                case 2: return tot[i];
                case 3: return andAll[i];
                default: return orAll[i];
            }
        }
        push(i, tl, tr);
        kids(i);
        long long tm = tl + (tr - tl) / 2;
        S a = query(Lc[i], tl, tm, ql, qr, kind), b = query(Rc[i], tm + 1, tr, ql, qr, kind);
        switch (kind) {
            case 0: return max(a, b);
            case 1: return min(a, b);
            case 2: return a + b;
            case 3: return a & b;
            default: return a | b;
        }
    }

    // amortized O(logU logU) -- a[i] &= X for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAndApply(long long l, long long r, T X) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAndApply: needs lo <= l <= r <= hi");
        if (l <= r) upd(root, lo, hi, l, r, X & FULL, 0);
    }

    // amortized O(logU logU) -- a[i] |= X for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeOrApply(long long l, long long r, T X) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeOrApply: needs lo <= l <= r <= hi");
        if (l <= r) upd(root, lo, hi, l, r, ~X & FULL, X & FULL);
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        return T(query(root, lo, hi, l, r, 0));
    }

    // O(logU) -- min of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMin(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeMin: needs lo <= l <= r <= hi");
        return T(query(root, lo, hi, l, r, 1));
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        return l > r ? S(0) : query(root, lo, hi, l, r, 2);
    }

    // O(logU) -- a[l] & ... & a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeAndQuery(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeAndQuery: needs lo <= l <= r <= hi");
        return l > r ? FULL : T(query(root, lo, hi, l, r, 3));
    }

    // O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeOrQuery(long long l, long long r) {
        if (l < lo || l > r || r > hi) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        return l > r ? T(0) : T(query(root, lo, hi, l, r, 4));
    }

    // O(logU) -- a[i] = v & FULL; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointAssign: needs lo <= i <= hi");
        set(root, lo, hi, i, v & FULL);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < lo || i > hi) throw out_of_range("pointGet: needs lo <= i <= hi");
        return rangeAndQuery(i, i);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmax: needs lo <= i <= hi");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < lo || i > hi) throw out_of_range("pointChmin: needs lo <= i <= hi");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(logU) -- a[i] = (a[i] + delta) & FULL; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T delta) {
        if (i < lo || i > hi) throw out_of_range("pointAdd: needs lo <= i <= hi");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mx[i] > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mx[i] >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mn[i] < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("leftmostLteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : firstPass(root, lo, hi, l, r, [&](int i) { return mn[i] <= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mx[i] > x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mx[i] >= x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLtX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLtX: needs lo <= l <= r <= hi");
        long long res = l > r ? NONE : lastPass(root, lo, hi, l, r, [&](int i) { return mn[i] < x; });
        return res == NONE ? lo - 1 : res;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostLteX(long long l, long long r, T x) {
        if (l < lo || l > r || r > hi) throw out_of_range("rightmostLteX: needs lo <= l <= r <= hi");
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