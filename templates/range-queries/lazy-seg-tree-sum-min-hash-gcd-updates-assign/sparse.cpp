// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/lazy-seg-tree-sum-min-hash-gcd-updates-assign/sparse.cpp
// @operations: isPalindrome leftmostLtX leftmostLteX pointAdd pointAssign pointChmax pointChmin pointGet rangeAssign rangeGcd rangeHash rangeHashReversed rangeMin rangeSum rangesEqual rightmostLtX rightmostLteX
// @data-structure-type: lazy-seg-tree
// @complexities:
//   isPalindrome: log(U)
//   leftmostLtX: log(U)
//   leftmostLteX: log(U)
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAssign: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   rangeHash: log(U)
//   rangeHashReversed: log(U)
//   rangeMin: log(U)
//   rangeSum: log(U)
//   rangesEqual: log(U)
//   rightmostLtX: log(U)
//   rightmostLteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mn[4*log(U)] fh[4*log(U)] bh[4*log(U)] g[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAssign) and range queries in O(logU), U = hi - lo + 1; each node keeps
// its sum, its min, its forward / backward hash (and B^size), its gcd over its range. Ranges inclusive [l, r];
// searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are
// zeros nobody reads), so a node of level s covers 2^s positions; children are created on demand as blocks of zeros,
// right before anything descends past a node, and a node's pending tags ("applied here, not yet to my children") go
// down as it is passed.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseLazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> mn{T(0)};
    vector<U64> fh{0};
    vector<U64> bh{0};
    vector<T> g{T(0)};
    vector<T> asg{T(0)};
    vector<char> hasAsg{0};
    vector<U64> PW, GS;  // PW[s] = B^(2^s), GS[s] = 1 + B + ... + B^(2^s - 1): per level

    static unsigned long long rnd() {
        static mt19937_64 g(chrono::steady_clock::now().time_since_epoch().count());
        return g();
    }
    // range hashes: mod the prime 2^61 - 1, with a base picked at random each run (so no test can be built against it)
    static constexpr unsigned long long HP = (1ULL << 61) - 1;
    static unsigned long long HB() {
        static unsigned long long b = (1ULL << 40) + rnd() % (HP - (1ULL << 41));
        return b;
    }
    static unsigned long long hmul(unsigned long long a, unsigned long long b) {
        __uint128_t c = (__uint128_t)a * b;
        unsigned long long r = (unsigned long long)(c & HP) + (unsigned long long)(c >> 61);
        r = (r & HP) + (r >> 61);
        return r >= HP ? r - HP : r;
    }
    static unsigned long long hadd(unsigned long long a, unsigned long long b) {
        return a + b >= HP ? a + b - HP : a + b;
    }
    static unsigned long long hraw(T v) {  // v as a residue (what an add changes a hash by, per position)
        long long r = (long long)v % (long long)HP;
        return r < 0 ? (unsigned long long)(r + (long long)HP) : (unsigned long long)r;
    }
    static unsigned long long hval(T v) {  // the hash of value v: v + an offset random per run, so no common value is 0
        static unsigned long long off = 1 + rnd() % (HP - 1);
        return hadd(hraw(v), off);
    }

    // O(1) -- all zeros over [lo, hi]; any long long range works (lo <= hi)
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        PW.assign(1, HB()), GS.assign(1, 1);
        for (int k = 0; k < D; k++) GS.push_back(hadd(hmul(GS[k], PW[k]), GS[k])), PW.push_back(hmul(PW[k], PW[k]));
        newZero(D);
    }

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), fh[ns[i]]), b = hadd(hmul(bh[ns[i]], p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
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

    // O(logU * logU) -- a[i] = v for i in [l, r]
    void rangeAssign(long long l, long long r, T v) {
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, g[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), fh[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(bh[ns[i]], p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logU) -- min of a[l..r]
    T rangeMin(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::max();
        for (int i = 0; i < c; i++) res = min(res, mn[ns[i]]);
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]
    S rangeSum(long long l, long long r) {
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
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
        U64 h = hmul(hval(T(0)), GS[s]);
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), mn.push_back(T(0)), fh.push_back(h), bh.push_back(h),
        g.push_back(T(0)), asg.push_back(T(0)), hasAsg.push_back(0);
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
        sm[p] = S(v), mn[p] = v, fh[p] = hval(v), bh[p] = hval(v), g[p] = v;
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        sm[x] = sm[a] + sm[b];
        mn[x] = min(mn[a], mn[b]);
        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);
        g[x] = gcd(g[a], g[b]);
    }

    void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        sm[x] = S(v) * k;
        mn[x] = v;
        fh[x] = bh[x] = hmul(hval(v), GS[s]);
        g[x] = v;  // (read through a gcd: |v|)
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
