// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/range-queries/lazy-seg-tree-hash-xor-and-or-gcd-run-alt-updates-assign/sparse.cpp
#include <bits/stdc++.h>
using namespace std;
using ll = long long;

// @operations: isPalindrome longestEqualRun maxAltSubseqSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeAssign rangeGcd rangeHash rangeHashReversed rangeOrQuery rangeXorQuery rangesEqual
// @data-structure-type: lazy-seg-tree
// @complexities:
//   isPalindrome: log(U)
//   longestEqualRun: log(U)
//   maxAltSubseqSum: log(U)
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAndQuery: log(U)
//   rangeAssign: log(U)*log(U) ?
//   rangeGcd: log(U) ?
//   rangeHash: log(U)
//   rangeHashReversed: log(U)
//   rangeOrQuery: log(U)
//   rangeXorQuery: log(U)
//   rangesEqual: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: fh[4*log(U)] bh[4*log(U)] xr[4*log(U)] an[4*log(U)] orr[4*log(U)] g[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: asg[4*log(U)] hasAsg[4*log(U)]
//   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Lazy segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; range updates (rangeAssign) and range queries in O(logU), U = hi - lo + 1; each node keeps
// its forward / backward hash (and B^size), its xor, its AND, its OR, its gcd, its first / last value and the equal
// runs at its ends and inside, its best alternating (+ - + ...) subsequence sum for each start / end sign over its
// range. Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions
// from lo (the ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created
// on demand as blocks of zeros, right before anything descends past a node, and a node's pending tags ("applied here,
// not yet to my children") go down as it is passed.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseLazySegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    struct Node {  // a node's fields side by side: a walk reads them together (faster than one array per field)
        U64 fh = 0;
        U64 bh = 0;
        S a00 = 0;
        S a01 = 0;
        S a10 = 0;
        S a11 = 0;
        long long pr = 0;
        long long sr = 0;
        long long br = 0;
        T xr = T(0);
        T an = ~T(0);
        T orr = T(0);
        T g = T(0);
        T fv = T(0);
        T lv = T(0);
        T asg = T(0);
        int L = 0;
        int R = 0;
        char hasAsg = 0;
    };
    vector<Node> nd{Node{}};  // node 0: none; node 1 is the root
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
    SparseLazySegTree(long long lo, long long hi) : first(lo), last(hi),
        D(hi > lo ? 64 - __builtin_clzll((unsigned long long)(hi - lo)) : 0) {
        PW.assign(1, HB()), GS.assign(1, 1);
        for (int k = 0; k < D; k++) GS.push_back(hadd(hmul(GS[k], PW[k]), GS[k])), PW.push_back(hmul(PW[k], PW[k]));
        newZero(D);
    }

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs lo <= l <= r <= hi, else throws out_of_range
    bool isPalindrome(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("isPalindrome: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), nd[ns[i]].fh), b = hadd(hmul(nd[ns[i]].bh, p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    long long longestEqualRun(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("longestEqualRun: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0];
        // (prefix run, suffix run, best, length)
        long long p = nd[t].pr, q = nd[t].sr, res = nd[t].br, k = 1LL << ls[0];
        T last = nd[t].lv;
        for (int i = 1; i < c; i++) {
            t = ns[i];
            long long w = 1LL << ls[i];
            bool j = last == nd[t].fv;
            res = max({res, nd[t].br, j ? q + nd[t].pr : 0LL});
            if (j && p == k) p += nd[t].pr;
            q = j && nd[t].sr == w ? q + nd[t].sr : nd[t].sr;
            k += w, last = nd[t].lv;
        }
        return res;
    }

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs lo <= l <= r <= hi, else
    // throws out_of_range
    S maxAltSubseqSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxAltSubseqSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{nd[ns[0]].a00, nd[ns[0]].a01, nd[ns[0]].a10, nd[ns[0]].a11};
        for (int i = 1; i < c; i++) a = altJoin(a, {nd[ns[i]].a00, nd[ns[i]].a01, nd[ns[i]].a10, nd[ns[i]].a11});
        return max(a[0], a[1]);
    }

    // O(logU * logU) -- a[i] += v; needs lo <= i <= hi, else throws out_of_range
    void pointAdd(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAdd: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, T(leaf(x) + v)), up(path);
    }

    // O(logU * logU) -- a[i] = v; needs lo <= i <= hi, else throws out_of_range
    void pointAssign(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointAssign: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, v), up(path);
    }

    // O(logU * logU) -- a[i] = max(a[i], v); needs lo <= i <= hi, else throws out_of_range
    void pointChmax(long long i, T v) {
        if (i < first || i > last) throw out_of_range("pointChmax: needs lo <= i <= hi");
        int path[64], x = leafOf(i, path);
        setLeaf(x, max(leaf(x), v)), up(path);
    }

    // O(logU * logU) -- a[i] = min(a[i], v); needs lo <= i <= hi, else throws out_of_range
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

    // O(logU) -- a[l] & ... & a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeAndQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAndQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = ~T(0);
        for (int i = 0; i < c; i++) res &= nd[ns[i]].an;
        return res;
    }

    // O(logU * logU) -- a[i] = v for i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    void rangeAssign(long long l, long long r, T v) {
        if (l < first || l > r || r > last) throw out_of_range("rangeAssign: needs lo <= l <= r <= hi");
        update(1, D, first, l, r, [&](int t, int s, long long) { applyAssign(t, s, v); });
    }

    // O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeGcd(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeGcd: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, nd[ns[i]].g);
        return res;
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // lo <= l <= r <= hi, else throws out_of_range
    U64 rangeHash(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHash: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), nd[ns[i]].fh);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs lo <= l <= r <= hi,
    // else throws out_of_range
    U64 rangeHashReversed(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHashReversed: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(nd[ns[i]].bh, p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeOrQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res |= nd[ns[i]].orr;
        return res;
    }

    // O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeXorQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeXorQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= nd[ns[i]].xr;
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, else throws out_of_range
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        if (l1 < first || l1 > r1 || r1 > last || l2 < first || l2 > r2 || r2 > last)
            throw out_of_range("rangesEqual: needs lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi");
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
        Node n;
        n.L = 0, n.R = 0, n.fh = h, n.bh = h, n.xr = T(0), n.an = T(0), n.orr = T(0), n.g = T(0), n.fv = T(0),
        n.lv = T(0), n.pr = 1LL << s, n.sr = 1LL << s, n.br = 1LL << s, n.a00 = S(0), n.a01 = s ? S(0) : NEG,
        n.a10 = s ? S(0) : NEG, n.a11 = S(0), n.asg = T(0), n.hasAsg = 0;
        nd.push_back(n);
        return (int)nd.size() - 1;
    }

    void kids(int x, int s) {  // create node x's children (blocks of zeros) if it has none yet
        if (nd[x].L) return;
        int a = newZero(s - 1), b = newZero(s - 1);
        nd[x].L = a, nd[x].R = b;
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
        if (l < m) collect(nd[x].L, s - 1, tl, l, r, ns, ls, ts, c);
        if (r >= m) collect(nd[x].R, s - 1, m, l, r, ns, ls, ts, c);
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
        if (l < m) update(nd[x].L, s - 1, tl, l, r, f);
        if (r >= m) update(nd[x].R, s - 1, m, l, r, f);
        pull(x, s);
    }

    int leafOf(long long i, int* path) {  // the leaf holding a[i]; path: the nodes above it top-down, every tag pushed
        int x = 1;
        long long tl = first;
        for (int s = D; s > 0; s--) {
            kids(x, s);
            push(x, s);
            path[D - s] = x;
            if (i >= tl + (1LL << (s - 1))) tl += 1LL << (s - 1), x = nd[x].R;
            else x = nd[x].L;
        }
        return x;
    }

    void up(const int* path) {  // recompute the nodes of path, deepest first (path[k] has level D - k)
        for (int k = D - 1; k >= 0; k--) pull(path[k], D - k);
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        nd[p].fh = hval(v), nd[p].bh = hval(v), nd[p].xr = v, nd[p].an = v, nd[p].orr = v, nd[p].g = v, nd[p].fv = v,
            nd[p].lv = v, nd[p].pr = 1,
        nd[p].sr = 1, nd[p].br = 1, nd[p].a00 = S(v), nd[p].a01 = NEG, nd[p].a10 = NEG, nd[p].a11 = -S(v);
    }

    T leaf(int p) const { return T(nd[p].xr); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = nd[x].L, b = nd[x].R;
        nd[x].fh = hadd(hmul(nd[a].fh, PW[s - 1]), nd[b].fh), nd[x].bh = hadd(hmul(nd[b].bh, PW[s - 1]), nd[a].bh);
        nd[x].xr = nd[a].xr ^ nd[b].xr;
        nd[x].an = nd[a].an & nd[b].an;
        nd[x].orr = nd[a].orr | nd[b].orr;
        nd[x].g = gcd(nd[a].g, nd[b].g);
        long long hl = 1LL << (s - 1);
        bool j = nd[a].lv == nd[b].fv;
        nd[x].br = max({nd[a].br, nd[b].br, j ? nd[a].sr + nd[b].pr : 0LL});
        nd[x].pr = j && nd[a].pr == hl ? nd[a].pr + nd[b].pr : nd[a].pr;
        nd[x].sr = j && nd[b].sr == hl ? nd[b].sr + nd[a].sr : nd[b].sr;
        nd[x].fv = nd[a].fv, nd[x].lv = nd[b].lv;
        array<S,
            4> c = altJoin({nd[a].a00, nd[a].a01, nd[a].a10, nd[a].a11}, {nd[b].a00, nd[b].a01, nd[b].a10, nd[b].a11});
        nd[x].a00 = c[0], nd[x].a01 = c[1], nd[x].a10 = c[2], nd[x].a11 = c[3];
    }

    void setAssign(int x, int s, T v) {  // every value under node x becomes v
        long long k = 1LL << s;
        nd[x].an = v;
        nd[x].orr = v;
        nd[x].fh = nd[x].bh = hmul(hval(v), GS[s]);
        nd[x].xr = k & 1 ? v : T(0);
        nd[x].g = v;  // (read through a gcd: |v|)
        nd[x].fv = nd[x].lv = v;
        nd[x].pr = nd[x].sr = nd[x].br = k;
        nd[x].a00 = S(v), nd[x].a11 = -S(v), nd[x].a01 = nd[x].a10 = k > 1 ? S(0) : NEG;
    }

    void applyAssign(int x, int s, T v) {
        setAssign(x, s, v);
        nd[x].asg = v, nd[x].hasAsg = 1;
    }

    void push(int x, int s) {  // hand node x's pending tags to its children
        int a = nd[x].L, b = nd[x].R, c = s - 1;  // (their level)
        if (nd[x].hasAsg) applyAssign(a, c, nd[x].asg), applyAssign(b, c, nd[x].asg), nd[x].hasAsg = 0;
    }
};
