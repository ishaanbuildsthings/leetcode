// Template by https://github.com/ishaanbuildsthings
// https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/seg-tree-sum-max-hash-pre-suf-best-npre-nsuf-xor-and-or-gcd-run-alt/sparse.cpp
// @operations: isPalindrome leftmostGtX leftmostGteX leftmostPrefixSumGtX leftmostPrefixSumGteX longestEqualRun maxAltSubseqSum maxPrefixSum maxSubarraySum maxSuffixSum minPrefixSum minSuffixSum pointAdd pointAssign pointChmax pointChmin pointGet rangeAndQuery rangeGcd rangeHash rangeHashReversed rangeMax rangeOrQuery rangeSum rangeXorQuery rangesEqual rightmostGtX rightmostGteX rightmostSuffixSumGtX rightmostSuffixSumGteX
// @data-structure-type: seg-tree
// @complexities:
//   isPalindrome: log(U)
//   leftmostGtX: log(U)
//   leftmostGteX: log(U)
//   leftmostPrefixSumGtX: log(U)
//   leftmostPrefixSumGteX: log(U)
//   longestEqualRun: log(U)
//   maxAltSubseqSum: log(U)
//   maxPrefixSum: log(U)
//   maxSubarraySum: log(U)
//   maxSuffixSum: log(U)
//   minPrefixSum: log(U)
//   minSuffixSum: log(U)
//   pointAdd: log(U)*log(U) ?
//   pointAssign: log(U)*log(U) ?
//   pointChmax: log(U)*log(U) ?
//   pointChmin: log(U)*log(U) ?
//   pointGet: log(U)
//   rangeAndQuery: log(U)
//   rangeGcd: log(U) ?
//   rangeHash: log(U)
//   rangeHashReversed: log(U)
//   rangeMax: log(U)
//   rangeOrQuery: log(U)
//   rangeSum: log(U)
//   rangeXorQuery: log(U)
//   rangesEqual: log(U)
//   rightmostGtX: log(U)
//   rightmostGteX: log(U)
//   rightmostSuffixSumGtX: log(U)
//   rightmostSuffixSumGteX: log(U)
//   build: 1
// @memory:
//   layout: sparse
//   node: sm[4*log(U)] mx[4*log(U)] fh[4*log(U)] bh[4*log(U)] pre[4*log(U)] suf[4*log(U)] best[4*log(U)] npre[4*log(U)] nsuf[4*log(U)] xr[4*log(U)] an[4*log(U)] orr[4*log(U)] g[4*log(U)] fv[4*log(U)] lv[4*log(U)] pr[4*log(U)] sr[4*log(U)] br[4*log(U)] a00[4*log(U)] a01[4*log(U)] a10[4*log(U)] a11[4*log(U)]
//   tags: none
//   other: PW[1*log(U)] GS[1*log(U)] children[8*log(U)]
//   note: per update, the nodes it visits (at most 4 per level, counting the children a push creates); node data per field, children L / R

// Segment tree with composable aggregates (sparse): any index range [lo, hi] (huge or negative is fine), every
// position starting at 0; point updates and range queries in O(logU), U = hi - lo + 1; each node keeps its sum, its
// max, its forward / backward hash (and B^size), its best prefix sum, its best suffix sum, its best subarray sum, its
// min prefix sum, its min suffix sum, its xor, its AND, its OR, its gcd, its first / last value and the equal runs at
// its ends and inside, its best alternating (+ - + ...) subsequence sum for each start / end sign over its range.
// Ranges inclusive [l, r]; searches return lo - 1 when nothing qualifies. The root covers 2^D >= U positions from lo
// (the ones past hi are zeros nobody reads), so a node of level s covers 2^s positions; children are created on
// demand as blocks of zeros, right before anything descends past a node.
// T: int, long long, ...; sums are kept in S (long long for small T).
template <typename T>
struct SparseSegTree {
    using S = conditional_t<(sizeof(T) < sizeof(long long)), long long, T>;
    using U64 = unsigned long long;
    static constexpr S NEG = numeric_limits<S>::lowest() / 4;  // (no alternating subsequence of that shape)
    long long first, last;  // the index range [lo, hi]
    int D;  // the root's level: 2^D >= hi - lo + 1
    vector<int> L{0}, R{0};  // children (node 0: none; node 1 is the root)
    vector<S> sm{0};
    vector<T> mx{T(0)};
    vector<U64> fh{0};
    vector<U64> bh{0};
    vector<S> pre{0};
    vector<S> suf{0};
    vector<S> best{0};
    vector<S> npre{0};
    vector<S> nsuf{0};
    vector<T> xr{T(0)};
    vector<T> an{~T(0)};
    vector<T> orr{T(0)};
    vector<T> g{T(0)};
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

    // O(logN) -- is a[l..r] a palindrome (its two hashes agree); needs lo <= l <= r <= hi, else throws out_of_range
    bool isPalindrome(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("isPalindrome: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 f = 0, b = 0, p = 1;
        for (int i = 0; i < c; i++) {
            f = hadd(hmul(f, PW[ls[i]]), fh[ns[i]]), b = hadd(hmul(bh[ns[i]], p), b), p = hmul(p, PW[ls[i]]);
        }
        return f == b;
    }

    // O(logU) -- the first i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mx[L[t]] > x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the first i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mx[L[t]] >= x) t = L[t];
                else t = R[t], tl += 1LL << s;
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] > x, or lo - 1 (a walk pruned by best prefix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostPrefixSumGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostPrefixSumGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + pre[t] > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + pre[L[t]] > S(x)) t = L[t];
                    else acc += sm[L[t]], t = R[t], tl += 1LL << s;
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // O(logU) -- first i in [l, r] with a[l] + ... + a[i] >= x, or lo - 1 (a walk pruned by best prefix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long leftmostPrefixSumGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("leftmostPrefixSumGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = 0; i < c; i++) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + pre[t] >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + pre[L[t]] >= S(x)) t = L[t];
                    else acc += sm[L[t]], t = R[t], tl += 1LL << s;
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // O(logN) -- the longest run of equal adjacent values in a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    long long longestEqualRun(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("longestEqualRun: needs lo <= l <= r <= hi");
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

    // O(logN) -- max of +b1 - b2 + b3 - ... over non-empty subsequences b of a[l..r]; needs lo <= l <= r <= hi, else
    // throws out_of_range
    S maxAltSubseqSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxAltSubseqSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        array<S, 4> a{a00[ns[0]], a01[ns[0]], a10[ns[0]], a11[ns[0]]};
        for (int i = 1; i < c; i++) a = altJoin(a, {a00[ns[i]], a01[ns[i]], a10[ns[i]], a11[ns[i]]});
        return max(a[0], a[1]);
    }

    // O(logN) -- max of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S maxPrefixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxPrefixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = pre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = max(res, acc + pre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- max sum of a non-empty contiguous subarray of a[l..r]; needs lo <= l <= r <= hi, else throws
    // out_of_range
    S maxSubarraySum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxSubarraySum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = best[ns[0]], q = suf[ns[0]];  // (q: the best sum ending at the right edge so far)
        for (int i = 1; i < c; i++) {
            int t = ns[i];
            res = max({res, best[t], q + pre[t]}), q = max(suf[t], sm[t] + q);
        }
        return res;
    }

    // O(logN) -- max of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S maxSuffixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("maxSuffixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = suf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = max(res, acc + suf[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- min of a[l] + ... + a[i] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S minPrefixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("minPrefixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = npre[ns[0]], acc = sm[ns[0]];
        for (int i = 1; i < c; i++) res = min(res, acc + npre[ns[i]]), acc += sm[ns[i]];
        return res;
    }

    // O(logN) -- min of a[i] + ... + a[r] over i in [l, r]; needs lo <= l <= r <= hi, else throws out_of_range
    S minSuffixSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("minSuffixSum: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        S res = nsuf[ns[c - 1]], acc = sm[ns[c - 1]];
        for (int i = c - 2; i >= 0; i--) res = min(res, acc + nsuf[ns[i]]), acc += sm[ns[i]];
        return res;
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
        for (int i = 0; i < c; i++) res &= an[ns[i]];
        return res;
    }

    // O(logU + logU) -- gcd of |a[l]|, ..., |a[r]|; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeGcd(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeGcd: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res = gcd(res, g[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] left to right (mod 2^61 - 1, random base): equal ranges hash equal; needs
    // lo <= l <= r <= hi, else throws out_of_range
    U64 rangeHash(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHash: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0;
        for (int i = 0; i < c; i++) res = hadd(hmul(res, PW[ls[i]]), fh[ns[i]]);
        return res;
    }

    // O(logN) -- hash of a[l..r] read right to left (= rangeHash of the reversed range); needs lo <= l <= r <= hi,
    // else throws out_of_range
    U64 rangeHashReversed(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeHashReversed: needs lo <= l <= r <= hi");
        int ns[128]{}, ls[128]{}, c = cover(l, r, ns, ls);  // (zeroed: l <= r gives at least one node)
        U64 res = 0, p = 1;
        for (int i = 0; i < c; i++) res = hadd(hmul(bh[ns[i]], p), res), p = hmul(p, PW[ls[i]]);  // (in front)
        return res;
    }

    // O(logU) -- max of a[l..r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeMax(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeMax: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = numeric_limits<T>::lowest();
        for (int i = 0; i < c; i++) res = max(res, mx[ns[i]]);
        return res;
    }

    // O(logU) -- a[l] | ... | a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeOrQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeOrQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res |= orr[ns[i]];
        return res;
    }

    // O(logU) -- a[l] + ... + a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    S rangeSum(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeSum: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        S res = S(0);
        for (int i = 0; i < c; i++) res += sm[ns[i]];
        return res;
    }

    // O(logU) -- a[l] ^ ... ^ a[r]; needs lo <= l <= r <= hi, else throws out_of_range
    T rangeXorQuery(long long l, long long r) {
        if (l < first || l > r || r > last) throw out_of_range("rangeXorQuery: needs lo <= l <= r <= hi");
        int ns[128], ls[128], c = cover(l, r, ns, ls);
        T res = T(0);
        for (int i = 0; i < c; i++) res ^= xr[ns[i]];
        return res;
    }

    // O(logN) -- are a[l1..r1] and a[l2..r2] equal (same length and hash); needs
    // lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi, else throws out_of_range
    bool rangesEqual(long long l1, long long r1, long long l2, long long r2) {
        if (l1 < first || l1 > r1 || r1 > last || l2 < first || l2 > r2 || r2 > last)
            throw out_of_range("rangesEqual: needs lo <= l1 <= r1 <= hi and lo <= l2 <= r2 <= hi");
        return r1 - l1 == r2 - l2 && rangeHash(l1, r1) == rangeHash(l2, r2);
    }

    // O(logU) -- the last i in [l, r] with a[i] > x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] > x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mx[R[t]] > x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- the last i in [l, r] with a[i] >= x, or lo - 1 (a walk pruned by the node max); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (!(mx[t] >= x)) continue;
            while (s) {  // walk down the passing node
                kids(t, s);
                s--;
                if (mx[R[t]] >= x) t = R[t], tl += 1LL << s;
                else t = L[t];
            }
            return tl;
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] > x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostSuffixSumGtX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGtX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + suf[t] > S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + suf[R[t]] > S(x)) t = R[t], tl += 1LL << s;
                    else acc += sm[R[t]], t = L[t];
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // O(logU) -- last i in [l, r] with a[i] + ... + a[r] >= x, or lo - 1 (a walk pruned by best suffix sums); needs
    // lo <= l <= r <= hi, else throws out_of_range
    long long rightmostSuffixSumGteX(long long l, long long r, T x) {
        if (l < first || l > r || r > last) throw out_of_range("rightmostSuffixSumGteX: needs lo <= l <= r <= hi");
        int ns[128], ls[128];
        long long ts[128];
        int c = cover(l, r, ns, ls, ts);
        S acc = 0;
        for (int i = c - 1; i >= 0; i--) {
            int t = ns[i], s = ls[i];
            long long tl = ts[i];
            if (acc + suf[t] >= S(x)) {
                while (s) {
                    kids(t, s);
                    s--;
                    if (acc + suf[R[t]] >= S(x)) t = R[t], tl += 1LL << s;
                    else acc += sm[R[t]], t = L[t];
                }
                return tl;
            }
            acc += sm[t];
        }
        return first - 1;
    }

    // ---- internals ----

    // A's part, then B's: the best alternating sums by (start sign, end sign) = (++, +-, -+, --)
    static array<S, 4> altJoin(const array<S, 4>& A, const array<S, 4>& B) {
        return {max({A[0], B[0], A[0] + B[2], A[1] + B[0]}), max({A[1], B[1], A[0] + B[3], A[1] + B[1]}),
                max({A[2], B[2], A[2] + B[2], A[3] + B[0]}), max({A[3], B[3], A[2] + B[3], A[3] + B[1]})};
    }

    int newZero(int s) {  // a new node: a block of 2^s zeros
        U64 h = hmul(hval(T(0)), GS[s]);
        L.push_back(0), R.push_back(0), sm.push_back(S(0)), mx.push_back(T(0)), fh.push_back(h), bh.push_back(h),
        pre.push_back(S(0)), suf.push_back(S(0)), best.push_back(S(0)), npre.push_back(S(0)), nsuf.push_back(S(0)),
        xr.push_back(T(0)), an.push_back(T(0)), orr.push_back(T(0)), g.push_back(T(0)), fv.push_back(T(0)),
        lv.push_back(T(0)), pr.push_back(1LL << s), sr.push_back(1LL << s), br.push_back(1LL << s), a00.push_back(S(0)),
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
        sm[p] = S(v), mx[p] = v, fh[p] = hval(v), bh[p] = hval(v), pre[p] = S(v), suf[p] = S(v), best[p] = S(v),
        npre[p] = S(v), nsuf[p] = S(v), xr[p] = v, an[p] = v, orr[p] = v, g[p] = v, fv[p] = v, lv[p] = v, pr[p] = 1,
        sr[p] = 1, br[p] = 1, a00[p] = S(v), a01[p] = NEG, a10[p] = NEG, a11[p] = -S(v);
    }

    T leaf(int p) const { return T(sm[p]); }  // the value at leaf p

    void pull(int x, int s) {  // recompute node x (level s) from its children
        int a = L[x], b = R[x];
        pre[x] = max(pre[a], sm[a] + pre[b]);
        suf[x] = max(suf[b], sm[b] + suf[a]);
        best[x] = max({best[a], best[b], suf[a] + pre[b]});
        npre[x] = min(npre[a], sm[a] + npre[b]);
        nsuf[x] = min(nsuf[b], sm[b] + nsuf[a]);
        sm[x] = sm[a] + sm[b];
        mx[x] = max(mx[a], mx[b]);
        fh[x] = hadd(hmul(fh[a], PW[s - 1]), fh[b]), bh[x] = hadd(hmul(bh[b], PW[s - 1]), bh[a]);
        xr[x] = xr[a] ^ xr[b];
        an[x] = an[a] & an[b];
        orr[x] = orr[a] | orr[b];
        g[x] = gcd(g[a], g[b]);
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
