// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-hash-pre-suf-best-xor-and-or-gcd-run-alt/template.cpp
// @operations: getAll isPalindrome leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeHash rangeHashReversed rangeOrQuery rangeSum rangeXorQuery rangesEqual rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: seg-tree
// @complexities:
//   getAll: N
//   isPalindrome: log(N)
//   leftmostPrefixSumGtX: log(N)
//   leftmostPrefixSumGteX: log(N)
//   longestEqualRun: log(N)
//   maxAltSubseqSum: log(N)
//   maxPrefixSum: log(N)
//   maxSubarraySum: log(N)
//   maxSuffixSum: log(N)
//   pointAdd: log(N)*log(U) ?
//   pointAssign: log(N)*log(U) ?
//   pointChmax: log(N)*log(U) ?
//   pointChmin: log(N)*log(U) ?
//   pointGet: log(N)
//   rangeAndQuery: log(N)
//   rangeGcd: log(N)+log(U) ?
//   rangeHash: log(N)
//   rangeHashReversed: log(N)
//   rangeOrQuery: log(N)
//   rangeSum: log(N)
//   rangeXorQuery: log(N)
//   rangesEqual: log(N)
//   rightmostSuffixSumGtX: log(N)
//   rightmostSuffixSumGteX: log(N)
//   build: N*log(U) ?
// @memory:
//   layout: 2n-iterative
//   node: sm[2*N] fh[2*N] bh[2*N] pre[2*N] suf[2*N] best[2*N] xr[2*N] an[2*N] orr[2*N] g[2*N] fv[2*N] lv[2*N] pr[2*N] sr[2*N] br[2*N] a00[2*N] a01[2*N] a10[2*N] a11[2*N]
//   tags: none
//   other: PW[1*log(N)]
//   note: leaves [n, 2n) hold each value's own aggregates; hash powers are per level (a covering node of level s has 2^s leaves)

// Segment tree with composable aggregates (2N iterative): point updates and range queries in O(logN); each node keeps
// its sum, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best subarray sum,
// its xor, its AND, its OR, its gcd, its first / last value and the equal runs at its ends and inside, its best
// alternating (+ - + ...) subsequence sum for each start / end sign over its range. All indices 0-based, ranges
// inclusive [l, r]; searches return -1 when nothing qualifies. Leaves tree[n..2n); a node used by a query or update
// is a perfect subtree of 2^s leaves (s = its level); an update rewrites a leaf, then its ancestors.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    int n, h;
    vector<S> sm;
    vector<U64> fh;
    vector<U64> bh;
    vector<S> pre;
    vector<S> suf;
    vector<S> best;
    vector<T> xr;
    vector<T> an;
    vector<T> orr;
    vector<T> g;
    vector<T> fv;
    vector<T> lv;
    vector<int> pr;
    vector<int> sr;
    vector<int> br;
    vector<S> a00;
    vector<S> a01;
    vector<S> a10;
    vector<S> a11;
    vector<U64> PW;  // PW[s] = B^(2^s): per level

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

    // O(N log U) -- arr: the initial array (non-empty)
    explicit SegTree(const vector<T>& arr) : n((int)arr.size()), h(n ? 32 - __builtin_clz(n) : 0) {
        sm.assign(2 * n, 0);
        fh.assign(2 * n, 0);
        bh.assign(2 * n, 0);
        pre.assign(2 * n, 0);
        suf.assign(2 * n, 0);
        best.assign(2 * n, 0);
        xr.assign(2 * n, T(0));
        an.assign(2 * n, ~T(0));
        orr.assign(2 * n, T(0));
        g.assign(2 * n, T(0));
        fv.assign(2 * n, T(0));
        lv.assign(2 * n, T(0));
        pr.assign(2 * n, 0);
        sr.assign(2 * n, 0);
        br.assign(2 * n, 0);
        a00.assign(2 * n, 0);
        a01.assign(2 * n, 0);
        a10.assign(2 * n, 0);
        a11.assign(2 * n, 0);
        for (int i = 0; i < n; i++) setLeaf(n + i, arr[i]);
        PW.assign(1, HB());
        while ((int)PW.size() <= h) PW.push_back(hmul(PW.back(), PW.back()));
        for (int x = n - 1; x > 0; x--) {
            int s = 0;
            for (int y = x; y < n; y <<= 1) s++;  // (x's level: down its left edge to the leaves)
            pull(x, s);
        }
    }

    // O(N) -- the whole array
    vector<T> getAll() const {
        vector<T> out(n);
        for (int i = 0; i < n; i++) out[i] = leaf(n + i);
        return out;
    }

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree)
    bool isPalindrome(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), fh[ns[i]]), b = hadd(hmul(bh[ns[i]], p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] > x, or -1 (a walk pruned by best prefix sums)
    int leftmostPrefixSumGtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] > S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] > S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- first i in [l, r] with a[l] + ... + a[i] >= x, or -1 (a walk pruned by best prefix sums)
    int leftmostPrefixSumGteX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i];
            if (acc + pre[t] >= S(x)) {
                while (t < n) {
                    if (acc + pre[2 * t] >= S(x)) t = 2 * t;
                    else acc += sm[2 * t], t = 2 * t + 1;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]
    int longestEqualRun(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        int t = ns[0], p = pr[t], q = sr[t], res = br[t], k = 1 << ls[0];  // (prefix run, suffix run, best, length)
        T last = lv[t];
        for (int i = 1; i < c; i++) {
            t = ns[i];
            int w = 1 << ls[i];
            bool j = last == fv[t];
            res = max({res, br[t], j ? q + pr[t] : 0});
            if (j && p == k) p += pr[t];
            q = j && sr[t] == w ? q + sr[t] : sr[t];
            k += w, last = lv[t];
        }
        return res;
    }

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]
    S maxAltSubseqSum(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]};
        for (int i = 1; i < c; i++) a = altJoin(a, {a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]});
        return max(a[0], a[1]);
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]
    S maxPrefixSum(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]
    S maxSubarraySum(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = best[ns[0]], q = suf[ns[0]];  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {
            int t = ns[i];
            res = max({res, best[t], q + pre[t]}), q = max(suf[t], sm[t] + q);
        }
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]
    S maxSuffixSum(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN * logU) -- a[i] += v
    void pointAdd(int i, T v) {
        int p = i + n;
        setLeaf(p, T(leaf(p) + v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = v
    void pointAssign(int i, T v) {
        int p = i + n;
        setLeaf(p, v), rebuild(p);
    }

    // O(logN * logU) -- a[i] = max(a[i], v)
    void pointChmax(int i, T v) {
        int p = i + n;
        setLeaf(p, max(leaf(p), v)), rebuild(p);
    }

    // O(logN * logU) -- a[i] = min(a[i], v)
    void pointChmin(int i, T v) {
        int p = i + n;
        setLeaf(p, min(leaf(p), v)), rebuild(p);
    }

    // O(logN) -- a[i]
    T pointGet(int i) {
        int p = i + n;
        return leaf(p);
    }

    // O(logN) -- a[l] & ... & a[r]
    T rangeAndQuery(int l, int r) {
        T res = ~T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res &= an[lo++];
            if (hi & 1) res &= an[--hi];
        }
        return res;
    }

    // O(logN + logU) -- gcd of |a[l]|, ..., |a[r]|
    T rangeGcd(int l, int r) {
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res = gcd(res, g[lo++]);
            if (hi & 1) res = gcd(res, g[--hi]);
        }
        return res;
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal
    U64 rangeHash(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), fh[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range)
    U64 rangeHashReversed(int l, int r) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(bh[ns[i]], p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logN) -- a[l] | ... | a[r]
    T rangeOrQuery(int l, int r) {
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res |= orr[lo++];
            if (hi & 1) res |= orr[--hi];
        }
        return res;
    }

    // O(logN) -- a[l] + ... + a[r]
    S rangeSum(int l, int r) {
        S res = S(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res += sm[lo++];
            if (hi & 1) res += sm[--hi];
        }
        return res;
    }

    // O(logN) -- a[l] ^ ... ^ a[r]
    T rangeXorQuery(int l, int r) {
        T res = T(0);
        for (int lo = l + n, hi = r + n + 1; lo < hi; lo >>= 1, hi >>= 1) {
            if (lo & 1) res ^= xr[lo++];
            if (hi & 1) res ^= xr[--hi];
        }
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash)
    bool rangesEqual(int l1, int r1, int l2, int r2) {
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] > x, or -1 (a walk pruned by best suffix sums)
    int rightmostSuffixSumGtX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] > S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] > S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // O(logN) -- last i in [l, r] with a[i] + ... + a[r] >= x, or -1 (a walk pruned by best suffix sums)
    int rightmostSuffixSumGteX(int l, int r, T x) {
        int ns[64]{}, ls[64]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i];
            if (acc + suf[t] >= S(x)) {
                while (t < n) {
                    if (acc + suf[2 * t + 1] >= S(x)) t = 2 * t + 1;
                    else acc += sm[2 * t + 1], t = 2 * t;
                }
                return t - n;
            }
            acc += sm[t];
        }
        return -1;
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    void setLeaf(int p, T v) {  // leaf p holds v alone
        sm[p] = S(v), fh[p] = hval(v), bh[p] = hval(v), pre[p] = S(v), suf[p] = S(v), best[p] = S(v), xr[p] = v,
        an[p] = v, orr[p] = v, g[p] = v, fv[p] = v, lv[p] = v, pr[p] = 1, sr[p] = 1, br[p] = 1, a00[p] = S(v),
        a01[p] = NEG, a10[p] = NEG, a11[p] = -S(v);
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = 2 * x, b = 2 * x + 1;
        pre[x] = max(pre[a], sm[a] + pre[b]);
        suf[x] = max(suf[b], sm[b] + suf[a]);
        best[x] = max({best[a], best[b], suf[a] + pre[b]});
        sm[x] = sm[a] + sm[b];
        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);
        xr[x] = xr[a] ^ xr[b];
        an[x] = an[a] & an[b];
        orr[x] = orr[a] | orr[b];
        g[x] = gcd(g[a], g[b]);
        int hl = 1 << (s - 1);
        bool j = lv[a] == fv[b];
        br[x] = max({br[a], br[b], j ? sr[a] + pr[b] : 0});
        pr[x] = j && pr[a] == hl ? pr[a] + pr[b] : pr[a];
        sr[x] = j && sr[b] == hl ? sr[b] + sr[a] : sr[b];
        fv[x] = fv[a], lv[x] = lv[b];
        array<S, 4> c = altJoin({a00[a], a01[a], a10[a], a11[a]}, {a00[b], a01[b], a10[b], a11[b]});
        a00[x] = c[0], a01[x] = c[1], a10[x] = c[2], a11[x] = c[3];
    }

    void rebuild(int p) {  // recompute every ancestor of leaf p
        for (int s = 1; p > 1; s++) p >>= 1, pull(p, s);
    }

    int cover(int l, int r, int* ns, int* ls) {  // the nodes covering a[l..r] left to right (ns) and their levels (ls)
        int c = 0, rc = 0, rn[32], rl[32];
        for (int lo = l + n, hi = r + n + 1, s = 0; lo < hi; lo >>= 1, hi >>= 1, s++) {
            if (lo & 1) ns[c] = lo++, ls[c++] = s;
            if (hi & 1) rn[rc] = --hi, rl[rc++] = s;
        }
        while (rc) rc--, ns[c] = rn[rc], ls[c++] = rl[rc];
        return c;
    }
};
