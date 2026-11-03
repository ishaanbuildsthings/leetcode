// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeAddArithSeq-rangeAssign-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeAddArithSeq rangeAssign rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAdd: log(U)
//   rangeAddArithSeq: log(U)
//   rangeAssign: log(U)
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)] as_[4*log(U)] ad[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAdd, rangeAddArithSeq, rangeAssign) and range queries in O(logU), U =
// hi - lo + 1; each node keeps its sum over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing
// qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level
// s covers 2^s positions; children are created on demand as blocks of zeros, right before anything descends past a
// node, and a node's pending tags ("applied here, not yet to my children") go down as it is passed.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseLazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> asg{T(0)};
    vector<char> hasAsg{0};
    vector<T> as_{T(0)};
    vector<T> ad{T(0)};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmin(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmin: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]; needs lo <= i <= hi, else throws out_of_range
    T pointGet(long long i) {
        if (i < first || i > last) throw out_of_range("pointGet: needs lo <= i <= hi");
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- a[i] += v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAdd(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAdd: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAP(t, s, v, T(0)); });
    }

    // O(logU) -- a[l + k] += start + k * step for k in [0, r - l]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAddArithSeq(long long l, long long r, T start, T step) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAddArithSeq: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long tl) { applyAP(t, s, T(start + step * T(tl - l)), step); });
    }

    // O(logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAssign(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), asg.push_back(T(0)), hasAsg.push_back(0),
        as_.push_back(T(0)), ad.push_back(T(0));
        return (int)L.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (L[x]) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        L[x] = a, R[x] = b;
    }

    // the nodes covering a[l..r] left to right: ns, their levels ls, their first indices ts
    int cover(long long l, long long r, int* ns, int* ls, long long* ts) {
        int c = 0;
        collect(1, D, first, l, r, ns, ls, ts, c);
        return c;
    }

    int cover(long long l, long long r, int* ns, int* ls) {
        long long ts[128];
        return cover(l, r, ns, ls, ts);
    }

    void collect(int x, int s, long long tl, long long l, long long r, int* ns, int* ls, long long* ts, int& c) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            ns[c] = x, ls[c] = s, ts[c++] = tl;
            return;
        }
        kids(x, s);
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(L[x], s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(R[x], s - 1, m, l, r, ns, ls, ts, c);
    }

    template <class F>  // f(node, level, first index) on every node covering a[l..r], then pull up
    void update(int x, int s, long long tl, long long l, long long r, const F& f) {
        if (l <= tl && tl + (1LL << s) - 1 <= r) {
            f(x, s, tl);
            return;
        }
        kids(x, s);
        push(x, s);
        long long m = tl + (1LL << (s - 1));
        if (l < m) update(L[x], s - 1, tl, l, r, f);
        if (r >= m) update(R[x], s - 1, m, l, r, f);
        pull(x, s);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            push(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = R[x];
            else x = L[x];
        }
        return x;
    }

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v);
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        sm[x] = sm[a] + sm[b];
    }

    void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        sm[x] = S(v) * k;
    }

    void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        asg[x] = v, hasAsg[x] = 1, as_[x] = ad[x] = T(0);
    }

    void setAP(int x, int s, T st, T d) {  // the k-th value under node x (k from 0) gains st + k * d
        S k = S(1) << s;
        sm[x] += S(st) * k + S(d) * (s ? (k >> 1) * (k - 1) : S(0));  // (k (k - 1) / 2 without overflowing first)
    }

    void applyAP(int x, int s, T st, T d) {
        setAP(x, s, st, d);
        as_[x] += st, ad[x] += d;
    }

    void push(int x, int s) {  // hand node x's pending tags to its children
        int a = L[x], b = R[x], c = s - 1;  // (their level)
        if (hasAsg[x]) applyAssign(a, c, asg[x]), applyAssign(b, c, asg[x]), hasAsg[x] = 0;
        if (as_[x] != T(0) || ad[x] != T(0)) {
            applyAP(a, c, as_[x], ad[x]), applyAP(b, c, T(as_[x] + ad[x] * (T(1) << c)), ad[x]);
            as_[x] = ad[x] = T(0);
        }
    }
};
