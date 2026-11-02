// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeAdd-rangeGcd-rangeSum/sparse.cpp
// @operations: pointAdd pointAssign pointChmax pointChmin pointGet rangeAdd rangeGcd rangeSum
// @data-structure-type: lazy-seg-tree
// @complexities:
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAdd: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   rangeSum: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] g[4*log(U)] fv[4*log(U)] lv[4*log(U)]
//   tags: add[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAdd) and range queries in O(logU), U = hi - lo + 1; each node keeps its
// sum, its gcd over its range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root
// covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s
// positions; children are created on demand as blocks of zeros, right before anything descends past a node, and a
// node's pending tags ("applied here, not yet to my children") go down as it is passed.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseLazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> g{T(0)};
    vector<T> fv{T(0)};
    vector<T> lv{T(0)};
    vector<T> add{T(0)};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU * logU) -- a[i] += v
    void pointAdd(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU * logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU * logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU * logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) {
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU * logU) -- a[i] += v for i in [l, r]
    void rangeAdd(long long l, long long r, T v) {
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAdd(t, s, v); });
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        T res = gcd(fv[ns[0]], g[ns[0]]), last = lv[ns[0]];  // the first value, then every adjacent difference
        for (int i = 1; i < c; i++) res = gcd(gcd(res, T(fv[ns[i]] - last)), g[ns[i]]), last = lv[ns[i]];
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), g.push_back(T(0)), fv.push_back(T(0)), lv.push_back(T(0)),
        add.push_back(T(0));
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
        sm[p] = S(v), g[p] = T(0), fv[p] = v, lv[p] = v;
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        sm[x] = sm[a] + sm[b];
        g[x] = gcd(gcd(g[a], g[b]), T(fv[b] - lv[a]));  // (the adjacent differences)
        fv[x] = fv[a], lv[x] = lv[b];
    }

    void setAdd(int x, int s, T v) {  // every value under node x gains v
        sm[x] += S(v) * (S(1) << s);
        fv[x] += v, lv[x] += v;
    }

    void applyAdd(int x, int s, T v) {
        setAdd(x, s, v);
        add[x] += v;
    }

    void push(int x, int s) {  // hand node x's pending tags to its children
        int a = L[x], b = R[x], c = s - 1;  // (their level)
        if (add[x] != T(0)) applyAdd(a, c, add[x]), applyAdd(b, c, add[x]), add[x] = T(0);
    }
};
