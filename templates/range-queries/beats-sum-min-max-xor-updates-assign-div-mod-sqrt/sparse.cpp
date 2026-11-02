// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/beats-sum-min-max-xor-updates-assign-div-mod-sqrt/sparse.cpp
// @operations: leftmostGtX leftmostGteX leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeFloorDiv rangeFloorSqrt rangeMax rangeMin rangeMod rangeSum rangeXorQuery rightmostGtX rightmostGteX rightmostLtX rightmostLteX
// @data-structure-type: beats
// @complexities:
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeAssign: log(U)
//   rangeFloorDiv: log(U)*log(U) amortized
//   rangeFloorSqrt: log(U)*log(log(U)) amortized
//   rangeMax: log(U)
//   rangeMin: log(U)
//   rangeMod: log(U)*log(U) amortized
//   rangeSum: log(U)
//   rangeXorQuery: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] mx[4*log(U)] xr[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates), amortized for the shrink walks; node data per field, children L / R

// Shrink segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAssign, rangeFloorDiv, rangeMod, rangeFloorSqrt) and range queries in
// O(logU), U = hi - lo + 1; each node keeps its sum, its min, its max, its xor over its range. Ranges inclusive [l,
// r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are
// zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as blocks of zeros,
// right before anything descends past a node, and a node's pending tags ("applied here, not yet to my children") go
// down as it is passed. mod / floor div / floor sqrt walk down every node whose max still changes.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseShrinkSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> mn{T(0)};
    vector<T> mx{T(0)};
    vector<T> xr{T(0)};
    vector<T> asg{T(0)};
    vector<char> hasAsg{0};

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseShrinkSegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        newZero(D);
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    long long leftmostGtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mx[L[t]] > x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    long long leftmostGteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mx[L[t]] >= x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mn[L[t]] < x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long leftmostLteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mn[L[t]] <= x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- a[i] += v
    void pointAdd(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU) -- a[i] = v
    void pointAssign(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU) -- a[i] = max(a[i], v)
    void pointChmax(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i] = min(a[i], v)
    void pointChmin(long long i, T v) {
        int path[64], x = leafOf(i, path);
        setLeaf(x, min(leaf(x), v)), up(path);
    }

    // O(logU) -- a[i]
    T pointGet(long long i) {
        int path[64];
        return leaf(leafOf(i, path));
    }

    // O(logU) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // amortized O(logU * logU) -- a[i] //= x for i in [l, r] (values >= 0; x >= 2, x = 1 does nothing)
    void rangeFloorDiv(long long l, long long r, T x) {
        if (x >= 2) update(1, D, first, l, r, [&](int t, int s, long long) { shrink(t, s, T(1), [x](T v) { return T(v / x); }); });
    }

    // amortized O(logU * loglogU) -- a[i] = floor(sqrt(a[i])) for i in [l, r] (values >= 0)
    void rangeFloorSqrt(long long l, long long r) {
        update(1, D, first, l, r, [&](int t, int s, long long) { shrink(t, s, T(2), isqrtT); });
    }

    // O(logU) -- max of a[l..r]
    T rangeMax(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::lowest();
        for (int i = 0; i < c; i++) res = max(res, mx[ns[i]]);
        return res;
    }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, mn[ns[i]]);
        return res;
    }

    // amortized O(logU * logU) -- a[i] %= x for i in [l, r] (values >= 0, x >= 1)
    void rangeMod(long long l, long long r, T x) {
        if (x >= 1) update(1, D, first, l, r, [&](int t, int s, long long) { shrink(t, s, x, [x](T v) { return T(v % x); }); });
    }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // O(logU) -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= xr[ns[i]];
        return res;
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max)
    long long rightmostGtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mx[R[t]] > x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max)
    long long rightmostGteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mx[R[t]] >= x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] < x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLtX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] < x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mn[R[t]] < x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] <= x, or lo - 1 (a walk pruned by the node min)
    long long rightmostLteX(long long l, long long r, T x) {
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mn[t] <= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s), push(t, s);
                s--;
                if (mn[R[t]] <= x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // ---- internals ----

    int newZero(int s) {  // a new node: a block of 2^s zeros
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), mn.push_back(T(0)), mx.push_back(T(0)), xr.push_back(T(0)),
        asg.push_back(T(0)), hasAsg.push_back(0);
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

    // floor(sqrt(v)) for v >= 0, exact for every 64-bit value
    static T isqrtT(T v) {
        T r = (T)sqrtl((long double)v);
        while (r > 0 && (__int128)r * r > v) r--;
        while ((__int128)(r + 1) * (r + 1) <= v) r++;
        return r;
    }

    template <class F>
    void shrink(int x, int s, T lim, const F& f) {  // every value v >= lim under node x (level s) becomes f(v)
        if (mx[x] < lim) return;
        if (s == 0) { setLeaf(x, f(mx[x])); return; }
        if (mn[x] == mx[x]) { applyAssign(x, s, f(mx[x])); return; }  // all equal: one assign
        kids(x, s);
        push(x, s);
        shrink(L[x], s - 1, lim, f), shrink(R[x], s - 1, lim, f);
        pull(x, s);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), mn[p] = v, mx[p] = v, xr[p] = v;
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        sm[x] = sm[a] + sm[b];
        mn[x] = min(mn[a], mn[b]);
        mx[x] = max(mx[a], mx[b]);
        xr[x] = xr[a] ^ xr[b];
    }

    void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        sm[x] = S(v) * k;
        mn[x] = v;
        mx[x] = v;
        xr[x] = k & 1 ? v : T(0);
    }

    void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        asg[x] = v, hasAsg[x] = 1;
    }

    void push(int x, int s) {  // hand node x's pending tags to its children
        int a = L[x], b = R[x], c = s - 1;  // (their level)
        if (hasAsg[x]) applyAssign(a, c, asg[x]), applyAssign(b, c, asg[x]), hasAsg[x] = 0;
    }
};
