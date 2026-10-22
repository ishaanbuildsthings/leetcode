// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeMin-rangeOrApply-rangeOrQuery/template.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeMin rangeOrApply rangeOrQuery
// @data-structure-type: beats
// @complexities:
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAndApply: log(N)*log(U) amortized
//   rangeAndQuery: log(N)
//   rangeMin: log(N)
//   rangeOrApply: log(N)*log(U) amortized
//   rangeOrQuery: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: mn[4*N] andAll[4*N] orAll[4*N]
//   tags: tagAnd[4*N] tagXor[4*N]
//   other: none
//   note: the and/or tags compose into one (and, xor) pair per node (or X is the pair (~X, X)); no range xor, see BitCountTree
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-AndApply-OrApply-Min-Max-Sum-AndQuery-OrQuery-pointSet.cpp

// Bitwise segment tree beats: range and= / or=, range min / and / or, point ops.
// All indices 0-based, ranges inclusive. Values live in [0, 2^bits). Every update is the map v -> (v & a) ^ x:
//   and X -> (X, 0)   or X -> (~X, X)
// and those compose into one (and, xor) tag. A tag may only be applied to a whole node when every bit the node's
// values DISAGREE on is merely kept (mixed & (~a | x) == 0): then every value moves by the same delta, so min just shift.
// Otherwise recurse; each recursion makes a mixed bit uniform, which pays for it.
// No range xor: xor flips a mixed bit without making it uniform, so it could recurse to every leaf, O(N) per op.
// For xor with sums use BitCountTree (per-bit counts), which needs no beats at all.
// T: int, long long, ....
template <typename T>
struct BitBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    T FULL;
    vector<T> mn, andAll, orAll, tagAnd, tagXor;

    // O(N)
    explicit BitBeats(const vector<T>& a, int bits = 20)
        : n((int)a.size()), FULL(T((T(1) << bits) - 1)), mn(4 * max(1, n)), andAll(4 * max(1, n), FULL), orAll(4 * max(1, n)), tagAnd(4 * max(1, n), FULL), tagXor(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void setLeaf(int i, T v) {
        mn[i] = andAll[i] = orAll[i] = v;
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    void build(int i, int tl, int tr, const vector<T>& a) {
        if (tl == tr) { setLeaf(i, a[tl]); return; }
        int tm = (tl + tr) / 2;
        build(2 * i, tl, tm, a), build(2 * i + 1, tm + 1, tr, a);
        pull(i);
    }

    void pull(int i) {
        int l = 2 * i, r = l + 1;
        mn[i] = min(mn[l], mn[r]);
        andAll[i] = andAll[l] & andAll[r], orAll[i] = orAll[l] | orAll[r];
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // only legal when the node's mixed bits are all kept, so every value shifts by the same delta
    void apply(int i, T a, T x) {
        T keep = (a ^ x) & FULL;
        T delta = (~orAll[i] & x & FULL) - (andAll[i] & ~keep & FULL);
        mn[i] += delta;
        andAll[i] = ((andAll[i] & a) ^ x) & FULL, orAll[i] = ((orAll[i] & a) ^ x) & FULL;
        tagAnd[i] = tagAnd[i] & a & FULL, tagXor[i] = ((tagXor[i] & a) ^ x) & FULL;
    }

    void push(int i, int tl, int tr) {
        if (tl == tr || (tagAnd[i] == FULL && tagXor[i] == 0)) return;
        apply(2 * i, tagAnd[i], tagXor[i]), apply(2 * i + 1, tagAnd[i], tagXor[i]);
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

    void upd(int i, int tl, int tr, int ql, int qr, T a, T x) {
        if (qr < tl || ql > tr || noEffect(i, a, x)) return;
        T mixed = (andAll[i] ^ orAll[i]) & FULL;
        if (ql <= tl && tr <= qr && (mixed & (~a | x) & FULL) == 0) { apply(i, a, x); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        upd(2 * i, tl, tm, ql, qr, a, x), upd(2 * i + 1, tm + 1, tr, ql, qr, a, x);
        pull(i);
    }

    void set(int i, int tl, int tr, int p, T v) {
        if (tl == tr) { setLeaf(i, v); return; }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        if (p <= tm) set(2 * i, tl, tm, p, v);
        else set(2 * i + 1, tm + 1, tr, p, v);
        pull(i);
    }

    // kind: 0 min, 1 and, 2 or; identities are valid because every value is in [0, FULL]
    S query(int i, int tl, int tr, int ql, int qr, int kind) {
        if (qr < tl || ql > tr) {
            switch (kind) {
                case 0: return S(FULL);
                case 1: return S(FULL);
                default: return S(0);
            }
        }
        if (ql <= tl && tr <= qr) {
            switch (kind) {
                case 0: return mn[i];
                case 1: return andAll[i];
                default: return orAll[i];
            }
        }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        S a = query(2 * i, tl, tm, ql, qr, kind), b = query(2 * i + 1, tm + 1, tr, ql, qr, kind);
        switch (kind) {
            case 0: return min(a, b);
            case 1: return a & b;
            default: return a | b;
        }
    }

    // amortized O(logN logU) -- a[i] &= X for i in [l, r]
    void rangeAndApply(int l, int r, T X) { if (l <= r && n) upd(1, 0, n - 1, l, r, X & FULL, 0); }

    // amortized O(logN logU) -- a[i] |= X for i in [l, r]
    void rangeOrApply(int l, int r, T X) { if (l <= r && n) upd(1, 0, n - 1, l, r, ~X & FULL, X & FULL); }

    // O(logN) -- min of a[l..r]
    T rangeMin(int l, int r) { return T(query(1, 0, n - 1, l, r, 0)); }

    // O(logN) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) { return l > r || !n ? FULL : T(query(1, 0, n - 1, l, r, 1)); }

    // O(logN) -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) { return l > r || !n ? T(0) : T(query(1, 0, n - 1, l, r, 2)); }

    // O(logN) -- a[i] = v & FULL
    void pointAssign(int i, T v) { if (n) set(1, 0, n - 1, i, v & FULL); }

    // O(logN) -- a[i]
    T pointGet(int i) { return rangeAndQuery(i, i); }

    // O(logN) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) { if (v > pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) { if (v < pointGet(i)) pointAssign(i, v); }

    // O(logN) -- a[i] = (a[i] + delta) & FULL
    void pointAdd(int i, T delta) { pointAssign(i, pointGet(i) + delta); }
};
