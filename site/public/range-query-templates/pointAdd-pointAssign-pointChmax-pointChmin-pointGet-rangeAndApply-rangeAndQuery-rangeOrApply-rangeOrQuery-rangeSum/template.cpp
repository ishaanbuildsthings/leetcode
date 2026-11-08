// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAndApply-rangeAndQuery-rangeOrApply-rangeOrQuery-rangeSum/template.cpp
// @operations: andAll getAll orAll pointAdd pointAssign pointChmax pointChmin pointGet rangeAndApply rangeAndQuery rangeOrApply rangeOrQuery rangeSum sumAll
// @data-structure-type: beats
// @complexities:
//   getAll: N
//   pointAdd: log(N) amortized
//   pointAssign: log(N) amortized
//   pointChmax: log(N) amortized
//   pointChmin: log(N) amortized
//   pointGet: log(N)
//   rangeAndApply: log(N)*log(U) amortized
//   rangeAndQuery: log(N)
//   rangeOrApply: log(N)*log(U) amortized
//   rangeOrQuery: log(N)
//   rangeSum: log(N)
//   sumAll: log(N)
//   andAll: log(N)
//   orAll: log(N)
//   build: N
// @memory:
//   layout: 4n-recursive
//   node: tot[4*N] andAgg[4*N] orAgg[4*N]
//   tags: tagAnd[4*N] tagXor[4*N]
//   other: none
//   note: the and/or tags compose into one (and, xor) pair per node (or X is the pair (~X, X)); no range xor, see BitCountTree
// @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/beats/range-AndApply-OrApply-Min-Max-Sum-AndQuery-OrQuery-pointSet.cpp

// Bitwise segment tree beats: range and= / or=, range sum / and / or, point ops.
// All indices 0-based, ranges inclusive. Values live in [0, 2^bits). Every update is the map v -> (v & a) ^ x:
//   and X -> (X, 0)   or X -> (~X, X)
// and those compose into one (and, xor) tag. A tag may only be applied to a whole node when every bit the node's
// values DISAGREE on is merely kept (mixed & (~a | x) == 0): then every value moves by the same delta, so sum just shift.
// Otherwise recurse; each recursion makes a mixed bit uniform, which pays for it.
// No range xor: xor flips a mixed bit without making it uniform, so it could recurse to every leaf, O(N) per op.
// For xor with sums use BitCountTree (per-bit counts), which needs no beats at all.
// T: int, long long, ...; sums accumulate in S (long long for small T).
template <typename T>
struct BitBeats {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    int n;
    T FULL;
    vector<T> andAgg, orAgg, tagAnd, tagXor;
    vector<S> tot;

    // O(N)
    explicit BitBeats(const vector<T>& a, int bits = 20)
        : n((int)a.size()), FULL(T((T(1) << bits) - 1)), andAgg(4 * max(1, n), FULL), orAgg(4 * max(1, n)), tagAnd(4 * max(1, n), FULL), tagXor(4 * max(1, n)), tot(4 * max(1, n)) {
        if (n) build(1, 0, n - 1, a);
    }

    void setLeaf(int i, T v) {
        andAgg[i] = orAgg[i] = v, tot[i] = v;
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
        tot[i] = tot[l] + tot[r];
        andAgg[i] = andAgg[l] & andAgg[r], orAgg[i] = orAgg[l] | orAgg[r];
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // only legal when the node's mixed bits are all kept, so every value shifts by the same delta (k = the node's length)
    void apply(int i, T a, T x, long long k) {
        T keep = (a ^ x) & FULL;
        T delta = (~orAgg[i] & x & FULL) - (andAgg[i] & ~keep & FULL);
        tot[i] += S(delta) * k;
        andAgg[i] = ((andAgg[i] & a) ^ x) & FULL, orAgg[i] = ((orAgg[i] & a) ^ x) & FULL;
        tagAnd[i] = tagAnd[i] & a & FULL, tagXor[i] = ((tagXor[i] & a) ^ x) & FULL;
    }

    void push(int i, int tl, int tr) {
        if (tl == tr || (tagAnd[i] == FULL && tagXor[i] == 0)) return;
        int tm = (tl + tr) / 2;
        apply(2 * i, tagAnd[i], tagXor[i], tm - tl + 1), apply(2 * i + 1, tagAnd[i], tagXor[i], tr - tm);
        tagAnd[i] = FULL, tagXor[i] = 0;
    }

    // (v & a) ^ x == v for every v in the node? keep bits are fine, flip bits never are, force-0 needs all 0,
    // force-1 needs all 1
    bool noEffect(int i, T a, T x) const {
        if (a & x & FULL) return false;
        if (~a & ~x & orAgg[i] & FULL) return false;
        if (~a & x & ~andAgg[i] & FULL) return false;
        return true;
    }

    void upd(int i, int tl, int tr, int ql, int qr, T a, T x) {
        if (qr < tl || ql > tr || noEffect(i, a, x)) return;
        T mixed = (andAgg[i] ^ orAgg[i]) & FULL;
        if (ql <= tl && tr <= qr && (mixed & (~a | x) & FULL) == 0) { apply(i, a, x, tr - tl + 1); return; }
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

    // kind: 0 sum, 1 and, 2 or; identities are valid because every value is in [0, FULL]
    S query(int i, int tl, int tr, int ql, int qr, int kind) {
        if (qr < tl || ql > tr) {
            switch (kind) {
                case 0: return S(0);
                case 1: return S(FULL);
                default: return S(0);
            }
        }
        if (ql <= tl && tr <= qr) {
            switch (kind) {
                case 0: return tot[i];
                case 1: return andAgg[i];
                default: return orAgg[i];
            }
        }
        push(i, tl, tr);
        int tm = (tl + tr) / 2;
        S a = query(2 * i, tl, tm, ql, qr, kind), b = query(2 * i + 1, tm + 1, tr, ql, qr, kind);
        switch (kind) {
            case 0: return a + b;
            case 1: return a & b;
            default: return a | b;
        }
    }

    // amortized O(logN logU) -- a[i] &= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeAndApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndApply: needs 0 <= l <= r < n");
        if (l <= r && n) upd(1, 0, n - 1, l, r, X & FULL, 0);
    }

    // amortized O(logN logU) -- a[i] |= X for i in [l, r]; needs 0 <= l <= r < n, else throws out_of_range
    void rangeOrApply(int l, int r, T X) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrApply: needs 0 <= l <= r < n");
        if (l <= r && n) upd(1, 0, n - 1, l, r, ~X & FULL, X & FULL);
    }

    // O(logN) -- a[l] + ... + a[r]; needs 0 <= l <= r < n, else throws out_of_range
    S rangeSum(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeSum: needs 0 <= l <= r < n");
        return l > r || !n ? S(0) : query(1, 0, n - 1, l, r, 0);
    }

    // O(logN) -- a[l] & ... & a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeAndQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeAndQuery: needs 0 <= l <= r < n");
        return l > r || !n ? FULL : T(query(1, 0, n - 1, l, r, 1));
    }

    // O(logN) -- a[l] | ... | a[r]; needs 0 <= l <= r < n, else throws out_of_range
    T rangeOrQuery(int l, int r) {
        if (l < 0 || l > r || r >= n) throw out_of_range("rangeOrQuery: needs 0 <= l <= r < n");
        return l > r || !n ? T(0) : T(query(1, 0, n - 1, l, r, 2));
    }

    // O(logN) amortized -- a[i] = v & FULL; needs 0 <= i < n, else throws out_of_range
    void pointAssign(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointAssign: needs 0 <= i < n");
        if (n) set(1, 0, n - 1, i, v & FULL);
    }

    // O(logN) -- a[i]; needs 0 <= i < n, else throws out_of_range
    T pointGet(int i) {
        if (i < 0 || i >= n) throw out_of_range("pointGet: needs 0 <= i < n");
        return rangeAndQuery(i, i);
    }

    void getAllRec(int i, int tl, int tr, vector<T>& out) {
        if (tl == tr) { out.push_back(andAgg[i]); return; }
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

    // O(logN) amortized -- a[i] = max(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmax(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmax: needs 0 <= i < n");
        if (v > pointGet(i)) pointAssign(i, v);
    }

    // O(logN) amortized -- a[i] = min(a[i], v); needs 0 <= i < n, else throws out_of_range
    void pointChmin(int i, T v) {
        if (i < 0 || i >= n) throw out_of_range("pointChmin: needs 0 <= i < n");
        if (v < pointGet(i)) pointAssign(i, v);
    }

    // O(logN) amortized -- a[i] = (a[i] + delta) & FULL; needs 0 <= i < n, else throws out_of_range
    void pointAdd(int i, T delta) {
        if (i < 0 || i >= n) throw out_of_range("pointAdd: needs 0 <= i < n");
        pointAssign(i, pointGet(i) + delta);
    }

    // O(log(N)) -- sum of the whole array a[0..n-1] (rangeSum(0, n - 1)); needs n >= 1, else throws out_of_range
    auto sumAll() {
        if (n < 1) throw out_of_range("sumAll: needs n >= 1");
        return rangeSum(0, n - 1);
    }

    // O(log(N)) -- AND of the whole array a[0..n-1] (rangeAndQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto andAll() {
        if (n < 1) throw out_of_range("andAll: needs n >= 1");
        return rangeAndQuery(0, n - 1);
    }

    // O(log(N)) -- OR of the whole array a[0..n-1] (rangeOrQuery(0, n - 1)); needs n >= 1, else throws out_of_range
    auto orAll() {
        if (n < 1) throw out_of_range("orAll: needs n >= 1");
        return rangeOrQuery(0, n - 1);
    }

};
