// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/isPalindrome-longestEqualRun-maxAltSubseqSum-pointAdd-pointAssign-pointChmax-pointChmin-pointGet-rangeHash-rangeHashReversed-rangesEqual/sparse.cpp
// @operations: isPalindrome longestEqualRun maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet rangeHash rangeHashReversed rangesEqual
// @data-structure-type: seg-tree
// @complexities:
//   isPalindrome: log(U)
//   longestEqualRun: log(U)
//   maxAltSubseqSum: log(U)
//   pointAdd: log(U)
//   pointAssign: log(U)
//   pointChmax: log(U)
//   pointChmin: log(U)
//   pointGet: log(U)
//   rangeHash: log(U)
//   rangeHashReversed: log(U)
//   rangesEqual: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: fh[4*log(U)] bh[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: none
//   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its forward /
// backward hash (and B^size), its first / last value and the equal runs at its ends and inside, its best alternating
// (+ - + ...) subsequence sum for each start / end sign over its range. Ranges inclusive [l, r]; searches return lo -
// 1 when nothing qualifies. The root covers 2^D >= U positions from lo (the ones past hi are zeros nobody reads), so
// a node of level s covers 2^s positions; children are created on demand as blocks of zeros, right before anything
// descends past a node.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<U64> fh{0};
    vector<U64> bh{0};
    vector<T> fv{T(0)};
    vector<T> lv{T(0)};
    vector<long long> pr{0};
    vector<long long> sr{0};
    vector<long long> br{0};
    vector<S> a00{0};
    vector<S> a01{0};
    vector<S> a10{0};
    vector<S> a11{0};
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
    SparseSegTree(long long lo, long long hi) : first(lo), last(hi), D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
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

    // O(logN) -- the longest run of equal adjacent values in a[l..r]
    long long longestEqualRun(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0];
        long long p = pr[t], q = sr[t], res = br[t], k = 1LL << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {
            t = ns[i];
            long long w = 1LL << ls[i];
            bool j = last == fv[t];
            res = max({res, br[t], j ? q + pr[t] : 0LL});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }
        return res;
    }

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(long long l, long long r) {
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]};
        for (int i = 1; i < c; i++) a = altJoin(a, {a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]});
        return max(a[0], a[1]);
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

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    int newZero(int s) {  // a new node: a block of 2^s zeros
        U64 h = hmul(hval(T(0)), GS[s]);
        L.push_back(0), R.push_back(0), fh.push_back(h), bh.push_back(h), fv.push_back(T(0)), lv.push_back(T(0)),
        pr.push_back(1LL << s), sr.push_back(1LL << s), br.push_back(1LL << s), a00.push_back(S(0)),
        a01.push_back(s ? S(0) : NEG), a10.push_back(s ? S(0) : NEG), a11.push_back(S(0));
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
        long long m = tl + (1LL << (s - 1));
        if (l < m) collect(L[x], s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(R[x], s - 1, m, l, r, ns, ls, ts, c);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
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
        fh[p] = hval(v), bh[p] = hval(v), fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1, a00[p] = S(v),
        a01[p] = NEG, a10[p] = NEG, a11[p] = -S(v);
    }

    T leaf(int p) const { return T(fv[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);
        long long hl = 1LL << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0LL});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
        array<S, 4> c = altJoin({a00[a], a01[a], a10[a], a11[a]}, {a00[b], a01[b], a10[b], a11[b]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
    }
};
